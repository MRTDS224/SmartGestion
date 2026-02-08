[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{12345678-1234-1234-1234-123456789012}
AppName=SmartGestion
AppVersion=1.0
AppPublisher=Antigravity
DefaultDirName={autopf}\SmartGestion
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
OutputBaseFilename=SmartGestionSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\SmartGestion\SmartGestion.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\SmartGestion\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\SmartGestion"; Filename: "{app}\SmartGestion.exe"
Name: "{autodesktop}\SmartGestion"; Filename: "{app}\SmartGestion.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SmartGestion.exe"; Description: "{cm:LaunchProgram,SmartGestion}"; Flags: nowait postinstall skipifsilent
