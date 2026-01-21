[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{12345678-1234-1234-1234-123456789012}
AppName=Madina Stock
AppVersion=1.0
AppPublisher=Antigravity
DefaultDirName={autopf}\MadinaStock
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputBaseFilename=MadinaStockSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\MadinaStock\MadinaStock.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\MadinaStock\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\Madina Stock"; Filename: "{app}\MadinaStock.exe"
Name: "{autodesktop}\Madina Stock"; Filename: "{app}\MadinaStock.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\MadinaStock.exe"; Description: "{cm:LaunchProgram,Madina Stock}"; Flags: nowait postinstall skipifsilent
