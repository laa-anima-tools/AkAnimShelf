proc
string
getActiveModelPanel()
{
    string $activeModelPanel = "";
string $activePanel = `getPanel - wf`;
if ("modelPanel" == `getPanel - to $activePanel`)
{
$activeModelPanel = $activePanel;
}
return $activeModelPanel;
}

string $currPanel = getActiveModelPanel();

if ($currPanel != "")
{
string $currCam = `modelEditor - q - camera  $currPanel
`;

string $FilmGateState = `camera - q - displayFilmGate $currCam
`;
string $ResolutionGateState = `camera - q - displayResolution $currCam
`;

if ($ResolutionGateState == 0) {
print "Turning Resolution Gate on";
camera -e -displayFilmGate off - displayResolution on -overscan 1.3 $currCam;
}
else {
print "Turning Resolution Gate off";
camera -e -displayFilmGate off - displayResolution off -overscan 1.0 $currCam;
}
}