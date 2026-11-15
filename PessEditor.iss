#define MyAppName "Pess Editor"
#define MyAppVersion "0.8.3"
#define MyAppPublisher "Pess"
#define MyAppExeName "PessEditor.exe"

[Setup]
AppId={{833ba00d-fe65-4158-9029-180e52410add}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Pess Editor
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=Resources\pess.ico
OutputDir=Build\Output
OutputBaseFilename=PessEditor_Setup_0.8.3
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "PessEditor.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSES\THIRD_PARTY_NOTICES.txt"; DestDir: "{app}\LICENSES"; Flags: ignoreversion

[Icons]
Name: "{group}\Pess Editor"; Filename: "{app}\PessEditor.exe"
Name: "{autodesktop}\Pess Editor"; Filename: "{app}\PessEditor.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PessEditor.exe"; Description: "Launch Pess Editor"; Flags: postinstall nowait skipifsilent