#define MyAppName "ULTRON Panel"
#define MyAppVersion "3.0"
#define MyAppPublisher "NATH-DEVcode"

[Setup]
AppId={{5A691A37-12EE-4E73-B737-554C54524F4E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\ULTRON Panel
DefaultGroupName=ULTRON Panel
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=UltronSetup-v3
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName=ULTRON Panel
SetupLogging=yes

[Files]
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*;*.bak;*.before-*"
Source: "data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*"
Source: "gui\ultron.py"; DestDir: "{app}\gui"; Flags: ignoreversion
Source: "gui\__init__.py"; DestDir: "{app}\gui"; Flags: ignoreversion
Source: "languages\*"; DestDir: "{app}\languages"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "skills\*"; DestDir: "{app}\skills"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__\*;*.bak"
Source: "themes\*"; DestDir: "{app}\themes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "config\ai.conf"; DestDir: "{app}\config"; Flags: ignoreversion skipifsourcedoesntexist
Source: "config\ia.conf"; DestDir: "{app}\config"; Flags: ignoreversion skipifsourcedoesntexist
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements-windows.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "setup-ultron.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: "INICIAR-ULTRON-WINDOWS.bat"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: checkedonce

[Icons]
Name: "{autoprograms}\ULTRON Panel"; Filename: "{app}\INICIAR-ULTRON-WINDOWS.bat"; WorkingDir: "{app}"
Name: "{autodesktop}\ULTRON Panel"; Filename: "{app}\INICIAR-ULTRON-WINDOWS.bat"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\setup-ultron.ps1"""; StatusMsg: "Configurando Python, dependencias y voz de ULTRON..."; Flags: runhidden waituntilterminated
Filename: "{app}\INICIAR-ULTRON-WINDOWS.bat"; Description: "Abrir ULTRON Panel"; Flags: postinstall nowait skipifsilent shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}\.venv"
