screengraphics set,640,480
varset beenbefore,0; varset beenbefore2,0
if set=0 goto "screenerror"
mousepresent mouse
if mouse=0 goto "mouseerror"
# gosub "findcd"
# delay 1000
animationplay logo,0,0,1,130,"winasoft.smk"
delay 2500
:mainmenu
mousesetxy 0,0
gosub "assignbitmaps"
animationopen mainmenu,2,"mainmenu.smk"
if beenbefore=0 animationopen bigtalk,2,"fbigtalk.smk"
if beenbefore=0 animationframes bigtalkframes,bigtalk
animationplay mmfadein,0,0,1,2,"mmfadein.smk"
animationtoscreen mainmenu,0,0
animationadvance mainmenu
gosub "assignmasks"
gosub "assignmouseareas"
:checkformouseclick
animationstilldelay status, mainmenu
if status=0 animationadvance mainmenu
if beenbefore=0 animationstilldelay status2, bigtalk
if bigtalkframes>0 if beenbefore=0 if status2=0 animationadvance bigtalk; compute bigtalkframes, bigtalkframes-1
inputcharordelay wheremouse,0
mousearea wheremouse2

if wheremouse2="data" bitmaptoscreentrans text1,64,30,0; varset flag5,1
if wheremouse2="openseq" bitmaptoscreentrans text3,264,155,0; varset flag1,1
if wheremouse2="tech" bitmaptoscreentrans text2,480,30,0; varset flag3,1 
if wheremouse2="asoft" bitmaptoscreentrans text4,252,278,0; varset flag2,1
if wheremouse2="film" bitmaptoscreentrans text5,52,362,0;varset flag4,1
if wheremouse2="exit" bitmaptoscreentrans text6,508,362,0;varset flag6,1  
 
if flag5=1 if wheremouse2<>"data" bitmaptoscreen mask5,64,30; varset flag5,0
if flag1=1 if wheremouse2<>"openseq" bitmaptoscreen mask1,264,155;varset flag1,0
if flag3=1 if wheremouse2<>"tech" bitmaptoscreen mask3,480,30; varset flag3,0
if flag2=1 if wheremouse2<>"asoft" bitmaptoscreen mask2,252,278; varset flag2,0
if flag4=1 if wheremouse2<>"film" bitmaptoscreen mask4,52,362; varset flag4,0
if flag6=1 if wheremouse2<>"exit" bitmaptoscreen mask6,508,362; varset flag6,0

if wheremouse="openseq" goto "fademainmenuout"; varset whichfade,1
if wheremouse="asoft" goto "fademainmenuout"; varset whichfade,2
if wheremouse="tech" goto "fademainmenuout"; varset whichfade,3
if wheremouse="film" goto "fademainmenuout"; varset whichfade,4
if wheremouse="data" goto "fademainmenuout"; varset whichfade,5
if wheremouse="exit" goto "fademainmenuout"; varset whichfade,6

goto "checkformouseclick"

:screenerror
screentext
text "You are unable to use INFODISK. Screen cannot display required resolution."
end

:mouseerror
screentext
text "You are unable to use INFODISK. Mouse required."
end

:fademainmenuout
if beenbefore=0 animationclose bigtalk; varset beenbefore,1
bitmaptoscreen mask5,64,30; varset flag5,0
bitmaptoscreen mask1,264,155;varset flag1,0
bitmaptoscreen mask3,480,30; varset flag3,0
bitmaptoscreen mask2,252,278; varset flag2,0
bitmaptoscreen mask4,52,362; varset flag4,0
bitmaptoscreen mask6,508,362; varset flag6,0
animationopen fade,0,"ffade%whichfade%.smk"
animationframes totalframes,fade
:fadeloop
animationstilldelay status, mainmenu
if status=0 animationadvance mainmenu
animationstilldelay status2, fade
if status2=0 animationadvance fade; compute totalframes, totalframes-1
if totalframes>0 goto "fadeloop"
animationclose fade
goto "%wheremouse%"

:openseq
gosub "clearmainmenu"
delay 2500
animationplay intro1,0,0,1,128,"musosp1.smk"
animationplay intro2,0,0,1,128,"newcred.smk"
animationplay intro3,0,0,1,128,"fasall.smk"
delay 2500
animationplay intro4,0,0,1,128,"mus5p2.smk"
delay 2500
animationplay blank,0,0,1,2,"blank.smk"
animationplay intro5,0,0,1,128,"coach.smk"
animationplay blank,0,0,1,2,"blank.smk"
animationplay intro6,0,0,1,128,"outmin.smk"
screenclear 0
goto "mainmenu"

:exit
gosub "clearmainmenu"
delay 2500
gosub "assignbitmaps2"
animationplay hypno,0,0,1,128,"fhypno.smk"
animationplay exit,0,0,1,0,"fbye1.smk"
animationopen beep,2,"fcount2.smk"
mouseadd "exit",548,421,42,21,0
systemdatetime dayofyear, "^j";systemdatetime year, "^Y";systemdatetime hour, "^H";systemdatetime minute, "^M";systemdatetime second, "^S"
compute dayofyear, 210-dayofyear; compute year, 1997-year; compute hour, 9-hour; compute minute, 60-minute; compute second, 60-second
compute secondstogo, dayofyear*86400
compute secondstemp, hour*3600
compute secondstogo, secondstogo+secondstemp
compute secondstemp, minute*60
compute secondstogo, secondstogo+secondstemp
compute secondstogo, secondstogo+second
if secondstogo<0 secondstogo=0

:printready
varset snpa,1
strlength stglength, secondstogo
compute stglength, 8-stglength
if stglength >0 strlpadzero eta,stglength,secondstogo

:printnumbers
varset snp,250
compute multiplier, snpa*14
compute snp,snp+multiplier
strpiece tempstr,snpa,1,eta
if tempstr=0 bitmaptoscreen number0,snp,375
if tempstr=1 bitmaptoscreen number1,snp,375
if tempstr=2 bitmaptoscreen number2,snp,375
if tempstr=3 bitmaptoscreen number3,snp,375
if tempstr=4 bitmaptoscreen number4,snp,375
if tempstr=5 bitmaptoscreen number5,snp,375
if tempstr=6 bitmaptoscreen number6,snp,375
if tempstr=7 bitmaptoscreen number7,snp,375
if tempstr=8 bitmaptoscreen number8,snp,375
if tempstr=9 bitmaptoscreen number9,snp,375
animationadvance beep
compute snpa, snpa+1
if snpa=9 goto "waitforexitclick"
goto "printnumbers"

:waitforexitclick
SystemTimer Start
compute Start, Start+1000
:hi
inputcharordelay whatclick,0
if whatclick="exit" animationclose beep; animationplay exit2,0,0,1,128,"fbye2.smk"; end
systemtimer end
if end<start goto "hi"
compute secondstogo, secondstogo-1
goto "printready"

:film
gosub "clearmainmenu"
delay 1000
animationopen wobble1,2,"wobble1.smk"; animationtoscreen wobble1,0,0
animationopen wobble2,2,"wobble2.smk"; animationtoscreen wobble2,0,0
animationopen wobble3,2,"wobble3.smk"; animationtoscreen wobble3,0,0
animationopen wobble4,2,"wobble4.smk"; animationtoscreen wobble4,0,0
animationopen wobble5,2,"wobble5.smk"; animationtoscreen wobble5,0,0
animationopen wobble6,2,"wobble6.smk"; animationtoscreen wobble6,0,0
animationopen wobble7,2,"wobble7.smk"; animationtoscreen wobble7,0,0
animationopen wobble8,2,"wobble8.smk"; animationtoscreen wobble8,0,0
animationopen wobble9,2,"wobble9.smk"; animationtoscreen wobble9,0,0

:filmmenu
mousesetxy 0,0
screenclear 0
varset wobbler1,0; varset wobbler2,0; varset wobbler3,0; varset wobbler4,0; varset wobbler5,0; varset wobbler6,0; varset wobbler7,0; varset wobbler8,0; varset wobbler9,0
if beenbefore2=0 animationplay clipsin,0,0,1,2,"fclipsin.smk"
if beenbefore2=1 animationplay clipsin2,0,0,1,2,"fclipin2.smk"
bitmapalloc clipsbackground,640,480
bitmapfromscreen clipsbackground,0,0
varset beenbefore2,1
gosub "setupclipboxes"
:choosecliploop
inputcharordelay wheremouse,0
mousearea wheremouse2

if wobbler1=1 if wheremouse2<>"wobble1" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble1; varset wobbler1,0
if wobbler2=1 if wheremouse2<>"wobble2" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble2; varset wobbler2,0
if wobbler3=1 if wheremouse2<>"wobble3" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble3; varset wobbler3,0
if wobbler4=1 if wheremouse2<>"wobble4" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble4; varset wobbler4,0
if wobbler5=1 if wheremouse2<>"wobble5" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble5; varset wobbler5,0
if wobbler6=1 if wheremouse2<>"wobble6" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble6; varset wobbler6,0
if wobbler7=1 if wheremouse2<>"wobble7" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble7; varset wobbler7,0
if wobbler8=1 if wheremouse2<>"wobble8" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble8; varset wobbler8,0
if wobbler9=1 if wheremouse2<>"wobble9" bitmaptoscreen clipsbackground,0,0; animationbacktostart wobble9; varset wobbler9,0

if wheremouse2="wobble1" animationstilldelay wobbledelay1, wobble1; if wobbledelay1=0 animationadvance wobble1; varset wobbler1,1 
if wheremouse2="wobble2" animationstilldelay wobbledelay2, wobble2; if wobbledelay2=0 animationadvance wobble2; varset wobbler2,1 
if wheremouse2="wobble3" animationstilldelay wobbledelay3, wobble3; if wobbledelay3=0 animationadvance wobble3; varset wobbler3,1 
if wheremouse2="wobble4" animationstilldelay wobbledelay4, wobble4; if wobbledelay4=0 animationadvance wobble4; varset wobbler4,1 
if wheremouse2="wobble5" animationstilldelay wobbledelay5, wobble5; if wobbledelay5=0 animationadvance wobble5; varset wobbler5,1 
if wheremouse2="wobble6" animationstilldelay wobbledelay6, wobble6; if wobbledelay6=0 animationadvance wobble6; varset wobbler6,1
if wheremouse2="wobble7" animationstilldelay wobbledelay7, wobble7; if wobbledelay7=0 animationadvance wobble7; varset wobbler7,1 
if wheremouse2="wobble8" animationstilldelay wobbledelay8, wobble8; if wobbledelay8=0 animationadvance wobble8; varset wobbler8,1 
if wheremouse2="wobble9" animationstilldelay wobbledelay9, wobble9; if wobbledelay9=0 animationadvance wobble9; varset wobbler9,1 

if wheremouse="wobble1" animationplay fgo1,0,0,1,128,"fgo1.smk"; delay 1000; animationplay blank,0,0,1,2,"blank.smk"; animationplay native,0,0,1,128,"maze.smk"; goto "filmmenu"
if wheremouse="wobble2" animationplay fgo2,0,0,1,128,"fgo2.smk"; delay 1000; animationplay blank,0,0,1,2,"blank.smk"; animationplay benson,0,0,1,128,"radioin.smk"; goto "filmmenu"
if wheremouse="wobble3" animationplay fgo3,0,0,1,128,"fgo3.smk"; delay 1000; animationplay blank,0,0,1,2,"blank.smk"; animationplay closeup,0,0,1,128,"pad.smk"; goto "filmmenu"
if wheremouse="wobble4" animationplay fgo4,0,0,1,128,"fgo4.smk"; delay 1000; animationplay blank,0,0,1,2,"blank.smk"; animationplay bridge,0,0,1,128,"bridge.smk"; goto "filmmenu"
if wheremouse="wobble5" animationplay fgo5,0,0,1,128,"fgo5.smk"; delay 1000; animationplay blank,0,0,1,2,"blank.smk"; animationplay shoot,0,0,1,128,"pilldie.smk"; goto "filmmenu"
if wheremouse="wobble6" animationplay fgo6,0,0,1,128,"fgo6.smk"; delay 1000; animationplay blank,0,0,1,2,"blank.smk"; animationplay tow,0,0,1,128,"bikebust.smk"; goto "filmmenu"
if wheremouse="wobble7" animationplay fgo7,0,0,1,128,"fgo7.smk"; delay 1000; animationplay blank,0,0,1,2,"blank.smk"; animationplay god,0,0,1,128,"statue.smk"; goto "filmmenu"
if wheremouse="wobble8" animationplay fgo8,0,0,1,128,"fgo8.smk"; delay 1000; animationplay blank,0,0,1,2,"blank.smk"; animationplay junk,0,0,1,128,"junkout.smk"; goto "filmmenu"
if wheremouse="wobble9" animationplay fgo9,0,0,1,128,"fgo9.smk"; delay 1000; goto "clearandmainmenu"
goto "choosecliploop"
end

:clearandmainmenu
bitmapfree clipsbackground
animationclose wobble1; animationclose wobble2; animationclose wobble3; animationclose wobble4; animationclose wobble5
animationclose wobble6; animationclose wobble7; animationclose wobble8; animationclose wobble9
mouseremove "wobble1"; mouseremove "wobble2"; mouseremove "wobble3"; mouseremove "wobble4"; mouseremove "wobble5"
mouseremove "wobble6"; mouseremove "wobble7"; mouseremove "wobble8"; mouseremove "wobble9"
screenclear 0
goto "mainmenu"

:tech
gosub "clearmainmenu"
delay 2500
animationplay slide1,0,0,1,128,"idfx4a.smk"
animationplay slide2,0,0,1,128,"idfx4b.smk"
animationplay slide3,0,0,1,128,"idfx4c.smk"
animationplay slide4,0,0,1,128,"idfx4d.smk"
animationplay slide5,0,0,1,128,"idfx4e.smk"
animationplay slide6,0,0,1,128,"idfx4f.smk"
animationplay slide7,0,0,1,128,"idfx4g.smk"
screenclear 0
goto "mainmenu"

:asoft
gosub "clearmainmenu"
delay 2500
animationplay scene3a,0,0,1,128,"fscene3b.smk"
animationplay scene3b,0,0,1,128,"fscene3a.smk"
animationplay scene3c,0,0,1,128,"fscene3c.smk"
animationplay scene3g,0,0,1,128,"fscene3g.smk"
screenclear 0
goto "mainmenu"

:data
gosub "clearmainmenu"
animationopen textmus,2,"mtextmus.smk"
animationopen data1,0,"ftext0.smk"
animationframes fdata1,data1
animationtoscreen data1,0,0
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
animationadvance data1; compute fdata1=fdata1-1
bitmapalloc pressspace,177,10
bitmapfromscreen pressspace,444,452
:mrloop
animationstilldelay data1delay,data1
if data1delay=0 animationadvance data1; compute fdata1=fdata1-1
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
if fdata1>0 goto "mrloop"
animationclose data1
animationopen data2,0,"ftext1.smk"
animationtoscreen data2,0,0
animationframes frames,data2
:data2loop
animationstilldelay data2delay,data2
if data2delay=0 animationadvance data2; compute frames=frames-1
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
if frames>0 goto "data2loop"
gosub "waitforspace"
animationclose data2
animationopen data3,0,"ftext2.smk"
animationtoscreen data3,0,0
animationframes frames,data3
:data3loop
animationstilldelay data3delay,data3
if data3delay=0 animationadvance data3; compute frames=frames-1
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
if frames>0 goto "data3loop"
gosub "waitforspace"
animationclose data3
animationopen data4,0,"ftext3.smk"
animationtoscreen data4,0,0
animationframes frames,data4
:data4loop
animationstilldelay data4delay,data4
if data4delay=0 animationadvance data4; compute frames=frames-1
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
if frames>0 goto "data4loop"
gosub "waitforspace"
animationclose data4
animationopen data5,0,"ftext4.smk"
animationtoscreen data5,0,0
animationframes frames,data5
:data5loop
animationstilldelay data5delay,data5
if data5delay=0 animationadvance data5; compute frames=frames-1
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
if frames>0 goto "data5loop"
gosub "waitforspace"
animationclose data5
animationopen data6,0,"ftext5.smk"
animationtoscreen data6,0,0
animationframes frames,data6
:data6loop
animationstilldelay data6delay,data6
if data6delay=0 animationadvance data6; compute frames=frames-1
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
if frames>0 goto "data6loop"
gosub "waitforspace"
animationclose data6
animationclose textmus
bitmapfree pressspace
screenclear 0
goto "mainmenu"

:waitforspace
bitmaptoscreen pressspace,444,452
systemtimer flash
compute flash, flash+500
:loopa
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
inputcharordelay click,0
if click="space" return
systemtimer check
if check<flash goto "loopa"
screenfilledbox 444,452,177,10,0
systemtimer flash
compute flash, flash+500
:loopb
inputcharordelay click,0
animationstilldelay textmusdelay,textmus
if textmusdelay=0 animationadvance textmus
if click="space" return
systemtimer check
if check<flash goto "loopb"
goto "waitforspace"

:findcd
bitmapalloc checkbg,0,0
textcolor 256
textbackcolor 255
texttranscolor 255
inputstrwin cdrom,-1,-1,1,"Please enter the letter of your CD-ROM drive: "
filecdrom check,"%cdrom%:/"
if check=1 bitmapfree checkbg; return
inputmsgwin check2,-1,-1,3,"Drive not detected. Enter again?"
if check2=1 goto "findcd"
if check2=2 end
 
:assignbitmaps

animationopen getbitmaps,2,"text.smk"
animationtoscreen getbitmaps,0,0
animationadvance getbitmaps
bitmapalloc text1,109,10
bitmapalloc text2,78,34
bitmapalloc text3,120,13
bitmapalloc text4,145,10
bitmapalloc text5,68,13
bitmapalloc text6,84,10
bitmapfromscreen text1,64,30
bitmapfromscreen text2,480,30
bitmapfromscreen text3,264,155
bitmapfromscreen text4,252,278
bitmapfromscreen text5,52,362
bitmapfromscreen text6,508,362
animationclose getbitmaps
return

:assignbitmaps2
animationopen getbitmaps2,2,"byet.smk"
animationtoscreen getbitmaps2,0,0
animationadvance getbitmaps
bitmapalloc number0,13,21
bitmapalloc number1,13,21
bitmapalloc number2,13,21
bitmapalloc number3,13,21
bitmapalloc number4,13,21
bitmapalloc number5,13,21
bitmapalloc number6,13,21
bitmapalloc number7,13,21
bitmapalloc number8,13,21
bitmapalloc number9,13,21
bitmapalloc outnow,139,21
bitmapfromscreen number0,425,212
bitmapfromscreen number1,221,225
bitmapfromscreen number2,244,225
bitmapfromscreen number3,267,225
bitmapfromscreen number4,290,225
bitmapfromscreen number5,313,225
bitmapfromscreen number6,336,225
bitmapfromscreen number7,359,225
bitmapfromscreen number8,383,225
bitmapfromscreen number9,405,225
bitmapfromscreen outnow,223,146
animationclose getbitmaps2
return
:assignmasks
bitmapalloc mask5,109,10
bitmapalloc mask3,78,34
bitmapalloc mask1,120,13
bitmapalloc mask2,145,10
bitmapalloc mask4,68,13
bitmapalloc mask6,84,10
bitmapfromscreen mask5,64,30
bitmapfromscreen mask3,480,30
bitmapfromscreen mask1,264,155
bitmapfromscreen mask2,252,278
bitmapfromscreen mask4,52,362
bitmapfromscreen mask6,508,362
return

:assignmouseareas
mouseadd "data",80,75,81,117,0
mouseadd "openseq",267,21,105,97,0
mouseadd "tech",456,89,125,103,0
mouseadd "asoft",151,225,345,41,0
mouseadd "film",169,319,109,113,0
mouseadd "exit",404,308,62,117,0
return

:clearmainmenu
bitmapfree text1
bitmapfree text2
bitmapfree text3
bitmapfree text4
bitmapfree text5
bitmapfree text6
bitmapfree mask1
bitmapfree mask2
bitmapfree mask3
bitmapfree mask4
bitmapfree mask5
bitmapfree mask6
mouseremove "data"
mouseremove "openseq"
mouseremove "tech"
mouseremove "asoft"
mouseremove "film"
mouseremove "exit"
animationclose mainmenu
return

:setupclipboxes
mouseadd "wobble1",28,81,123,93,0
mouseadd "wobble2",182,81,123,93,0
mouseadd "wobble3",335,81,123,93,0
mouseadd "wobble4",488,81,123,93,0
mouseadd "wobble5",28,201,123,93,0
mouseadd "wobble6",182,201,123,93,0
mouseadd "wobble7",335,201,123,93,0
mouseadd "wobble8",488,201,123,93,0
mouseadd "wobble9",255,357,135,45,0
return
