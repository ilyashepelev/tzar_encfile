#ifndef UNICODE
#define UNICODE
#endif 
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <WinSock2.h>
#include <WS2tcpip.h>
#include <shobjidl.h> 
#include <windows.h>
#include <windowsx.h> 
 
#pragma comment(lib, "Ws2_32.lib")


#define IDB_Button1 1
#define IDB_Button2 2
#define ID_BTNFILE 3

#define IDB_Button4 4
#define ID_RADIOBTN1 5
#define ID_RADIOBTN2 6
#define ID_RECV 7
#define IDB_Input 8

#define ID_LISTVIEW 9



typedef struct
{
    TCHAR achName[MAX_PATH];
    TCHAR achIp[MAX_PATH];
} Player;

Player Roster[] =
{

    {TEXT("Мой айпи"), TEXT("127.0.0.1")},
    {TEXT("Иван Петрович"), TEXT("192.168.1.254")},

};

RECT rcl;

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);

HWND static_label, hwndButton;
HWND hwndInput1;
HWND hwndInput2;
HWND hwndButton2;
HWND BtnFILE;
HWND BtnGROUPBOX;
HWND BtnRADIOBTN1;
HWND BtnRADIOBTN2;
HWND hwndButtonRecv;
HWND hWndList;
HWND static_label2;


int recv_file() {

    WORD wVersionRequested;
    WSADATA wsaData;
    int err;

    wVersionRequested = MAKEWORD(2, 2);

    err = WSAStartup(wVersionRequested, &wsaData);
    if (err != 0) {
        exit(1);
    }

    struct in_addr local_ip;
    inet_pton(AF_INET, "0.0.0.0", &local_ip);
    unsigned short local_port = 8888;

    struct sockaddr_in local_addr_in;
    memset(&local_addr_in, 0, sizeof(struct sockaddr_in));
    local_addr_in.sin_addr = local_ip;
    local_addr_in.sin_port = htons(local_port);
    local_addr_in.sin_family = AF_INET;

    struct sockaddr* local_addr = (struct sockaddr*)&local_addr_in;

    struct sockaddr remote_addr;
    int remote_addr_len = sizeof(struct sockaddr);


    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);


    bind(sock, local_addr, sizeof(struct sockaddr));
    listen(sock, SOMAXCONN);
    int sock_accept = accept(sock, &remote_addr, &remote_addr_len);



    char file_name[255];

    memset(file_name, 0, sizeof(file_name));

    recv(sock_accept, file_name, sizeof(file_name), 0);

    char tt[2] = "1";
    send(sock_accept, tt, sizeof(tt), 0);



    FILE* f = fopen(file_name, "wb");



    char file_fragment[50000];
    long long file_size = 0;
    int fragment_size;

    while (1)
    {
        fragment_size = recv(sock_accept, file_fragment, sizeof(file_fragment), 0);
        if (fragment_size <= 0) {
            break;
        }
        fwrite(file_fragment, 1, fragment_size, f);
        file_size = file_size + fragment_size;
        printf("\rrecv_bytes: %lld\n", file_size);
    }



    fclose(f);
    closesocket(sock_accept);
    closesocket(sock);
    WSACleanup();
    return 0;
}

int send_file(char* ip_address, char* file_address, char* name_of_file, int len_name) {



    FILE* f = fopen(file_address, "rb");

    if (f == NULL) {
        return 1;
    }


    fseek(f, 0, SEEK_END);
    long long file_size = _ftelli64(f);
    fseek(f, 0, SEEK_SET);

    WORD wVersionRequested;
    WSADATA wsaData;
    int err;

    wVersionRequested = MAKEWORD(2, 2);

    err = WSAStartup(wVersionRequested, &wsaData);
    if (err != 0) {
        fclose(f);
        return 2;
    }

    struct in_addr remote_ip;

    if ((inet_pton(AF_INET, ip_address, &remote_ip)) <= 0) {
        WSACleanup();
        fclose(f);
        return 3;
    }


    unsigned short remote_port = 8888;

    struct sockaddr_in remote_addr_in;
    memset(&remote_addr_in, 0, sizeof(struct sockaddr_in));
    remote_addr_in.sin_addr = remote_ip;
    remote_addr_in.sin_port = htons(remote_port);
    remote_addr_in.sin_family = AF_INET;

    struct sockaddr* remote_addr = (struct sockaddr*)&remote_addr_in;
    int remote_addrlen = sizeof(struct sockaddr);

    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (sock == INVALID_SOCKET) {
        SetWindowText(static_label, L"ERR sock");
        closesocket(sock);
        WSACleanup();
        fclose(f);

        return 4;
    }

    int err_c = connect(sock, remote_addr, remote_addrlen);

    //------------------------------------------------------------------file_name
 

    send(sock, name_of_file, len_name, 0);

    char b[2];
    recv(sock, b, sizeof(b), 0);

    if (err_c == 0)
    {
        char file_fragment[50000];
        int send_bytes;
        int fragment_size;
        long long total_send = 0;
        int progress;

        while (1) {
            fragment_size = fread(file_fragment, 1, sizeof(file_fragment), f);
            if (fragment_size == 0) {

                break;

            }

            send_bytes = send(sock, file_fragment, fragment_size, 0);
            total_send = total_send + send_bytes;

        }



    }
    else {
        closesocket(sock);
        WSACleanup();
        fclose(f);

        return 5;
    }


    closesocket(sock);
    WSACleanup();
    fclose(f);
    return 0;
}


int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE, PWSTR pCmdLine, int nCmdShow)
{



    // Register the window class.
    const wchar_t CLASS_NAME[] = L"TZAR Window Class";

    WNDCLASS wc = { };

    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;

    RegisterClass(&wc);

    // Create the window.

    HWND hwnd = CreateWindowEx(
        0,                              // Optional window styles.
        CLASS_NAME,                     // Window class
        L"TZAR",    // Window text
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,            // Window style

        // Size and position
        CW_USEDEFAULT, CW_USEDEFAULT, 600, 400,

        NULL,       // Parent window    
        NULL,       // Menu
        hInstance,  // Instance handle
        NULL        // Additional application data
    );

    if (hwnd == NULL)
    {
        return 0;
    }

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);


    // Run the message loop.
    MSG msg = { };
    while (GetMessage(&msg, NULL, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
    switch (uMsg)
    {

    case WM_CREATE:
        GetClientRect(hwnd, &rcl);
        static_label = CreateWindow(L"Static", L"Кому:", WS_CHILD | WS_VISIBLE,
            280,
            10,
            rcl.right - 290,
            20, hwnd, 0, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), 0);


        hwndInput1 = CreateWindow(
            L"EDIT", 0, WS_BORDER | WS_CHILD | WS_VISIBLE,
            280,
            30,
            rcl.right - 290,
            20, hwnd, (HMENU)IDB_Input, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);

        static_label2 = CreateWindow(L"Static", L"Файл:", WS_CHILD | WS_VISIBLE,
            280,
            80,
            rcl.right - 290,
            20, hwnd, 0, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), 0);

        hwndInput2 = CreateWindow(
            L"EDIT", 0, WS_BORDER | WS_CHILD | WS_VISIBLE,
            280,
            100,
            rcl.right - 290,
            20, hwnd, (HMENU)IDB_Input, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);



        BtnFILE = CreateWindow(
            L"BUTTON", L"ВЫБРАТЬ", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            280,         // x position 
            130,         // y position 
            90,        // Button width
            30,        // Button height
            hwnd, (HMENU)ID_BTNFILE, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);


        BtnGROUPBOX = CreateWindow(
            L"BUTTON", L"режим",
            WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_GROUPBOX,
            280,         // x position 
            180,         // y position 
            rcl.right - 290,        // Button width
            90,        // Button height
            hwnd, 0, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);


        //---------------------------------------ID_RADIOBTN

        BtnRADIOBTN1 = CreateWindow(
            L"BUTTON", L"отправить файл", WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON,
            300,         // x position 
            200,         // y position 
            200,        // Button width
            30,        // Button height
            hwnd, (HMENU)ID_RADIOBTN1, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);

        SendMessage(BtnRADIOBTN1, BM_SETCHECK, BST_CHECKED, 0);



        BtnRADIOBTN2 = CreateWindow(
            L"BUTTON", L"принять файл", WS_CHILD | WS_VISIBLE | BS_AUTORADIOBUTTON,
            300,         // x position 
            230,         // y position 
            200,        // Button width
            30,        // Button height
            hwnd, (HMENU)ID_RADIOBTN2, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);

        //---------------------------------------ID_RADIOBTN


        hwndButtonRecv = CreateWindow(
            L"BUTTON", L"ПРИНЯТЬ", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            rcl.right - 300,         // x position 
            rcl.bottom - 40,         // y position 
            90,        // Button width
            30,        // Button height
            hwnd, (HMENU)ID_RECV, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);
        Button_Enable(hwndButtonRecv, FALSE);


        hwndButton = CreateWindow(
            L"BUTTON", L"ОТПРАВИТЬ", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            rcl.right - 200,         // x position 
            rcl.bottom - 40,         // y position 
            90,        // Button width
            30,        // Button height
            hwnd, (HMENU)IDB_Button1, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);

        hwndButton2 = CreateWindow(
            L"BUTTON", L"ВЫХОД", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            rcl.right - 100,         // x position 
            rcl.bottom - 40,         // y position 
            90,        // Button width
            30,        // Button height
            hwnd, (HMENU)IDB_Button2, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);

        hWndList = CreateWindow(
            L"LISTBOX",
            L"",
            WS_CHILD | WS_VISIBLE | LBS_STANDARD | LBS_WANTKEYBOARDINPUT | WS_VSCROLL,
            10, 10,
            250, rcl.bottom - 10,
            hwnd, (HMENU)ID_LISTVIEW, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);

        SendMessage(hWndList, WM_SETREDRAW, FALSE, 0L);

        for (int i = 0; i < ARRAYSIZE(Roster); i++) {
            SendMessage(hWndList, LB_ADDSTRING, 0, (LPARAM)Roster[i].achName);

        }


        SendMessage(hWndList, WM_SETREDRAW, TRUE, 0L);

        InvalidateRect(hWndList, NULL, TRUE);



    case WM_SETFOCUS:
    {
        SetFocus(hWndList);
        return 0;
    }

    case WM_COMMAND:


        switch (wParam)
        {
        case IDB_Button1:
        {


            Button_Enable(hwndButton, FALSE);

            char line[255];
            GetWindowTextA(hwndInput1, line, sizeof(line));

            char line2[255];
            GetWindowTextA(hwndInput2, line2, sizeof(line2));

        //--------------------------------------------

            char dd[255];

            int j = 0;
            for (int i = 0; i < strlen(line2); i++)
            {

                if (line2[i] == '\\') {
                    memset(dd, 0, sizeof(dd));
                    j = 0;
                    continue;
                }
                dd[j] = line2[i];
                j++;
              
            }
            dd[j] = 0;

         
           
        
           int is_send = send_file(line, line2, dd, j);

            switch (is_send)
            {

            case 0:
                MessageBox(hwnd, L"Файл отправлен успешно!", L"TZAR", MB_OK);
                SetWindowText(hwndInput1, L"");
                SetWindowText(hwndInput2, L"");
                break;
            case 1:
                MessageBox(hwnd, L"Ошибка файла!", L"TZAR", MB_OK);
                break;
            case 2:
                MessageBox(hwnd, L"Ошибка WSAStartup!", L"TZAR", MB_OK);
                break;
            case 3:
                MessageBox(hwnd, L"Ошибка адреса (IP)!", L"TZAR", MB_OK);
                break;
            case 4:
                MessageBox(hwnd, L"Ошибка сокета!", L"TZAR", MB_OK);
                break;
            case 5:
                MessageBox(hwnd, L"Ошибка подключения!", L"TZAR", MB_OK);
                break;
            default:
                MessageBox(hwnd, L"Непредвиденная ошибка", L"TZAR", MB_OK);
                break;
            }



            Button_Enable(hwndButton, TRUE);

            return 0;
        }

        case ID_RECV:
        {
            Button_Enable(hwndButtonRecv, FALSE);

            recv_file();
            Button_Enable(hwndButtonRecv, TRUE);
            MessageBox(hwnd, L"Файл успешно загружен!", L"TZAR", MB_OK);
          
            return 0;
        }

        case IDB_Button2:
        {
            if (MessageBox(hwnd, L"Выйти из программы?", L"TZAR", MB_OKCANCEL) == IDOK)
            {
                DestroyWindow(hwnd);
            }
            // Else: User canceled. Do nothing.
            return 0;
        }

        case ID_BTNFILE:
        {
            HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED |
                COINIT_DISABLE_OLE1DDE);

            if (SUCCEEDED(hr))
            {
                IFileOpenDialog* pFileOpen;

                // Create the FileOpenDialog object.
                hr = CoCreateInstance(CLSID_FileOpenDialog, NULL, CLSCTX_ALL,
                    IID_IFileOpenDialog, reinterpret_cast<void**>(&pFileOpen));

                if (SUCCEEDED(hr))
                {
                    // Show the Open dialog box.
                    hr = pFileOpen->Show(NULL);

                    // Get the file name from the dialog box.
                    if (SUCCEEDED(hr))
                    {
                        IShellItem* pItem;
                        hr = pFileOpen->GetResult(&pItem);
                        if (SUCCEEDED(hr))
                        {
                            PWSTR pszFilePath;
                            hr = pItem->GetDisplayName(SIGDN_FILESYSPATH, &pszFilePath);

                            // Display the file name to the user.
                            if (SUCCEEDED(hr))
                            {

                                SetWindowText(hwndInput2, pszFilePath);
                                CoTaskMemFree(pszFilePath);
                            }
                            pItem->Release();
                        }
                    }
                    pFileOpen->Release();
                }
                CoUninitialize();
            }
            return 0;
        }


        case ID_RADIOBTN1:
        {

            Button_Enable(hwndButton, TRUE);
            Button_Enable(BtnFILE, TRUE);
            Button_Enable(hwndButtonRecv, FALSE);

            return 0;
        }

        case ID_RADIOBTN2:
        {
            SetWindowText(hwndInput1, L"");
            SetWindowText(hwndInput2, L"");
            Button_Enable(hwndButtonRecv, TRUE);
            Button_Enable(hwndButton, FALSE);
            Button_Enable(BtnFILE, FALSE);
            return 0;
        }

        return 0;


        }


        switch (LOWORD(wParam)) {


            case ID_LISTVIEW:
            {

                if (HIWORD(wParam) == LBN_DBLCLK)
                {


                    int pos = (int)SendMessage(hWndList, LB_GETCURSEL, 0, 0);

                    SetWindowText(hwndInput1, Roster[pos].achIp);

                }

                return 0;

            }

            return 0;
            }



        return 0;

    case WM_PAINT:
    {

        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hwnd, &ps);

        FillRect(hdc, &ps.rcPaint, (HBRUSH)(COLOR_WINDOW + 1));

        EndPaint(hwnd, &ps);
        return 0;

    }


    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    }


    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}
