Welcome to the Myst 1.0 README file


This file contains technical information regarding sound cards, 
video cards, display drivers, memory, and any known hardware 
incompatibilities.  Please read this file in its entirety before 
contacting Broderbund Technical Support.    

SOUND CARDS
-----------
Myst takes full advantage of the software volume control features 
available on MPC sound cards.  Consequently, it is essential that
you review the following information to see if your sound device is 
affected: 



Pro Audio Spectrum 16 owners 
---------------------------- 
Make sure that you have updated to the most recent PAS 16 drivers. 

Also make sure that the "MVSound.sys" line in your config.sys file 
includes these arguments in addition to any others: 
 
T:1 W:0 
 
----------------------------------------------------------------- 
 
Pro Audio Spectrum + owners 
--------------------------- 
 
In the directory on your hard drive where you installed Myst,
you'll find a file called "Myst.ini".  Open it up using a 
plain-text editor such as "Notepad" (provided with Windows) and
add the line:  
 
VolCurve=4Bit 
 
----------------------------------------------------------------- 
 
All sound cards with software volume control 
-------------------------------------------- 
 
If volume output is set very low in your autoexec.bat file or in  
your mixer application, Myst might be quite loud in comparison to  
other applications.  This is because Myst takes full advantage of  
software volume control within the game.  You may want to adjust 
your speaker output to accommodate this increased volume.
 
----------------------------------------------------------------- 

MEMORY
------

Myst is designed to use the full capabilities of your computer.  
It is highly recommended that you do not use other programs (or keep 
other program windows open) while playing Myst.  In addition, the 
performance of Myst may vary according to the capabilities of your 
CD-ROM drive (as well as your other hardware).

For Myst to function properly we recommend that  Windows  have a total 
of 10,000 KB of free memory.  This amount may be a combination of 
physical and virtual memory.  To check the amount of free memory
currently available to Windows, begin at the Windows Program Manager.  
Select "About Program Manager" from the "Help" menu.  At the bottom of 
the information box will be a line titled "Memory" which will show 
the amount free memory (in KB) available to Windows.  

If the total memory available to Windows is less than 10,000 KB try 
increasing the size of the Windows swap file (virtual memory).  
To increase the size of the Windows swap file follow these steps:

     1.  Begin at the Windows Program Manager.  Open the "Control Panel" 
         icon, located in the "Main" program group.

     2.  Double click on the icon named "386 Enhanced."  

     3.  Click on the button labeled "Virtual Memory . . ."  

     4.  Click on the button labeled "Change."  A "New Settings" dialog 
         box will open.

     5.  Increase the size of your swap file in the "New Size" dialog box. 
         Click OK.

     6.  A dialog box will appear asking if you would like to restart 
         Windows.  Click "Restart Windows."


VIDEO CARDS AND DISPLAY DRIVERS
-------------------------------
 
If you are experiencing video problems while playing Myst then try 
updating to a more recent version of your display driver.  

Microsoft SVGA driver 
---------------------

If you are using the Microsoft SVGA driver and the menu bar does not
completely hide then try using the driver that came with your video card.


HeadLand SVGA Card
-------------------

If you are using the HeadLand SVGA local bus video card and are 
experiencing problems with QuickTime movies not being placed correctly
on the screen try updating to the most recent version of your display 
driver. 

Also try making the following adjustments to your QTW.INI file, located
in your \WINDOWS directory:

If there is a line labeled:   

optimize=hardware

then change it to read:

optimize=driver

If neither of the above lines exist then add the following lines:

[Video]
optimize=driver


 

ATI Mach 32 Driver
------------------

Users of the ATI Mach 32 driver should update to the newest version 
of the driver.  Broderbund has successfully tested Myst with version 2.2.  


MISCELLANEOUS
-------------

COREL SCSI!
-----------

If you are encountering problems installing or running Myst while using
COREL SCSI! try updating to the most recent drivers.  


BRODERBUND TECHNICAL SUPPORT
----------------------------

To contact Broderbund Technical Support call (415) 382-4700 between the
hours of 7 a.m. and 5 p.m. (Pacific Time), Monday through Friday.
 
