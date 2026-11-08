; IBRA LENS — منصّب الوندوز (Inno Setup 6)
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppName "IBRA LENS"
#define MyAppExe "IBRA LENS.exe"
#define MyPublisher "Ibrahim Al-Khazraji (IBRAPROGRAM)"

[Setup]
AppId={{6E0B1C3A-7F4D-4E8B-9A51-1B0A1E450001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyPublisher}
AppPublisherURL=https://t.me/ibraprogram
AppSupportURL=https://github.com/ibrata2/ibra-lens
AppUpdatesURL=https://github.com/ibrata2/ibra-lens/releases
DefaultDirName={autopf}\IBRA LENS
DefaultGroupName=IBRA LENS
DisableProgramGroupPage=yes
OutputDir=..\Output
OutputBaseFilename=IBRA-LENS-{#MyAppVersion}-Setup
SetupIconFile=..\ibralens\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExe}
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
CloseApplications=yes
RestartApplications=no
DiskSpanning=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Desktop shortcut / اختصار على سطح المكتب"; GroupDescription: "Shortcuts:"
Name: "contextmenu"; Description: "Right-click on images: Find similar with IBRA LENS / ابحث عن مثيلها"; GroupDescription: "Explorer:"

[Files]
Source: "..\dist\IBRA LENS\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\IBRA LENS"; Filename: "{app}\{#MyAppExe}"
Name: "{group}\Uninstall IBRA LENS"; Filename: "{uninstallexe}"
Name: "{autodesktop}\IBRA LENS"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\image\shell\IBRALens"; ValueType: string; ValueName: "MUIVerb"; ValueData: "ابحث عن مثيلها بـ IBRA LENS"; Flags: uninsdeletekey; Tasks: contextmenu
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\image\shell\IBRALens"; ValueType: string; ValueName: "Icon"; ValueData: """{app}\{#MyAppExe}"",0"; Tasks: contextmenu
Root: HKA; Subkey: "Software\Classes\SystemFileAssociations\image\shell\IBRALens\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExe}"" ""%1"""; Tasks: contextmenu

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "Run IBRA LENS / شغّل البرنامج"; Flags: nowait postinstall
