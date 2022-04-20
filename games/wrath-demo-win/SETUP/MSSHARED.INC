GLOBAL SharedFileNeedsCopying AS INTEGER

DECLARE FUNCTION WCompareVersion (szVer1$, szVer2$) AS INTEGER

DECLARE FUNCTION FindSharedFileFromPath (szField$, szVersion$) AS STRING

DECLARE FUNCTION SearchForLocationForSharedFile (szRegDbKey$, szWinIniSect$, szWinIniKey$, iWinIniField%, szDefault$, szVersion$) AS STRING



'' returns: 1 if szVer1$ > szVer2$;  0 if equal;  -1 if szVer1$ < szVer2$
''
FUNCTION WCompareVersion (szVer1$, szVer2$) STATIC AS INTEGER
    IF szVer1$ = "" THEN
        IF szVer2$ = "" THEN
            WCompareVersion = 0
        ELSE
            WCompareVersion = -1
        END IF
    ELSEIF szVer2$ = "" THEN
        WCompareVersion = 1
    ELSE
        WCompareVersion = 0
        FOR i% = 1 TO 4 STEP 1
            piece1& = GetVersionNthField(szVer1$, i%)
            piece2& = GetVersionNthField(szVer2$, i%)
            IF piece1& > piece2& THEN
                WCompareVersion = 1
                GOTO _WCV_END
            ELSEIF piece1& < piece2& THEN
                WCompareVersion = -1
                GOTO _WCV_END
            END IF
        NEXT i%
    END IF
_WCV_END:
END FUNCTION


'' private to this file - needed in next api
''
FUNCTION FindSharedFileFromPath(szField$, szVersion$) STATIC AS STRING
    FindSharedFileFromPath = ""
    SharedFileNeedsCopying = 0
    IF szField$ <> "" THEN
        IF DoesFileExist(szField$, OF_EXIST) = 0 THEN
            szFile$ = STRING$(32, 32)

            IF FParseFATPathIntoPieces(szField$, NULL, 0, NULL, 0, szFile$, 31) <> 0 THEN
                szField$ = FindFileUsingFileOpen(szFile$)
            ELSE
                szField$ = ""
            END IF
            szFile$ = ""
        END IF

        IF szField$ <> "" THEN
            IF WCompareVersion(GetVersionOfFile(szField$), szVersion$) >= 0 THEN
                FindSharedFileFromPath = szField$
            ELSEIF IsFileWritable(szField$) <> 0 THEN
                SharedFileNeedsCopying = 1
                FindSharedFileFromPath = szField$
            END IF

            szField$ = ""
        END IF
    END IF
END FUNCTION


FUNCTION SearchForLocationForSharedFile (szRegDbKey$, szWinIniSect$, szWinIniKey$, iWinIniField%, szDefault$, szVersion$) STATIC AS STRING

    SearchForLocationForSharedFile = szDefault$

'$IFDEF    REG_DB_ENABLED
    IF szRegDbKey$ <> "" THEN
        szField$ = GetRegKeyValue(szRegDbKey$)
        szFile$ = FindSharedFileFromPath(szField$, szVersion$)
        IF szFile$ <> "" THEN
            SearchForLocationForSharedFile = szFile$
            szFile$ = ""
            GOTO _SFLSFS_END
        END IF
    END IF
'$ENDIF '' REG_DB_ENABLED

    IF szWinIniSect$ <> "" AND szWinIniKey$ <> "" THEN
        szWinIniLine$ = GetIniKeyString("WIN.INI", szWinIniSect$, szWinIniKey$)
        IF szWinIniLine$ <> "" THEN
            szField$ = GetNthFieldFromIniString(szWinIniLine$, iWinIniField%)
            szWinIniLine$ = ""
            szFile$ = FindSharedFileFromPath(szField$, szVersion$)
            IF szFile$ <> "" THEN
                SearchForLocationForSharedFile = szFile$
                szFile$ = ""
                GOTO _SFLSFS_END
            END IF
        END IF
    END IF

    '' return value is still szDefault$ - assume it is writable
    SharedFileNeedsCopying = 1
    IF DoesFileExist(szDefault$, OF_EXIST) <> 0 THEN
        IF WCompareVersion(GetVersionOfFile(szDefault$), szVersion$) >= 0 THEN
            SharedFileNeedsCopying = 0
        END IF
    END IF

_SFLSFS_END:

END FUNCTION

