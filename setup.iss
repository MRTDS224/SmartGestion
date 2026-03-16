[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{12345678-1234-1234-1234-123456789012}
AppName=SmartGestion
AppVersion=1.1
AppPublisher=Antigravity
DefaultDirName={autopf}\SmartGestion
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputBaseFilename=SmartGestionSetup1.1
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\SmartGestion\SmartGestion1.1.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SmartGestion\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\SmartGestion"; Filename: "{app}\SmartGestion1.1.exe"
Name: "{autodesktop}\SmartGestion"; Filename: "{app}\SmartGestion1.1.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SmartGestion1.1.exe"; Description: "{cm:LaunchProgram,SmartGestion}"; Flags: nowait postinstall skipifsilent
