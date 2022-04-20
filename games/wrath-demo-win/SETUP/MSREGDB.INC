'***************************************************************************
'****************     registration database api's    ***********************
'***************************************************************************

'$DEFINE REG_DB_ENABLED

const REG_SZ               = 1
const HKEY_CLASSES_ROOT    = 1
const ERROR_SUCCESS        = 0


DECLARE FUNCTION EercErrorHandler LIB "mscomstf.dll" (grc%, fVital%, sz1$, sz2$, sz3$) AS INTEGER
CONST GRC_API_FAILED       = 104

DECLARE FUNCTION RegOpenKey LIB "SHELL.DLL" (hKey&, szSubKey$, phkResult AS POINTER TO LONG) AS LONG
DECLARE FUNCTION RegCreateKey LIB "shell.dll" (hKey&, szSubKey$, phkResult AS POINTER TO LONG) AS LONG
DECLARE FUNCTION RegDeleteKey LIB "shell.dll" (hKey&, szSubKey$) AS LONG
DECLARE FUNCTION RegCloseKey LIB "shell.dll" (hKey&) AS LONG
DECLARE FUNCTION RegQueryValue LIB "shell.dll" (hKey&, szSubKey$, szValue$, lpcb AS POINTER TO LONG) AS LONG
DECLARE FUNCTION RegSetValue LIB "shell.dll" (hKey&, szSubKey$, dwType&, szValue$, cbValue&) AS LONG
DECLARE FUNCTION RegEnumKey LIB "shell.dll" (HkEY&, dwIndex&, szBuffer$, dwBufferSize&) AS LONG


DECLARE SUB CreateRegKey(szKey$)
DECLARE SUB CreateRegKeyValue(szKey$, szValue$)
DECLARE SUB SetRegKeyValue(szKey$, szValue$)
DECLARE SUB DeleteRegKey(szKey$)
DECLARE FUNCTION GetRegKeyValue(szKey$) AS STRING
DECLARE FUNCTION DoesRegKeyExist(szKey$) AS INTEGER


'NOTE: All keys are assumed to be subkeys of HKEY_CLASSES_ROOT. Therefore,
'the key HKEY_CLASSES_ROOT\key1\key2 would simply be written as key1\key2
'for these api's.


'**************************************************************************
SUB CreateRegKey(szKey$) STATIC
    DIM phKey AS LONG

    IF RegCreateKey(HKEY_CLASSES_ROOT, szKey$, VARPTR(phKey)) > ERROR_SUCCESS THEN
        i% = EercErrorHandler(GRC_API_FAILED, 1, "CreateRegKey", NULL, NULL)
'$ifdef DEBUG
        StfApiErr saeFail, "CreateRegKey", szKey$
'$endif ''DEBUG
        ERROR STFERR
    END IF

    IF RegCloseKey(phKey) > ERROR_SUCCESS THEN
        i% = EercErrorHandler(GRC_API_FAILED, 1, "CreateRegKey", NULL, NULL)
'$ifdef DEBUG
        StfApiErr saeFail, "CreateRegKey", szKey$
'$endif ''DEBUG
        ERROR STFERR
    END IF
END SUB


'**************************************************************************
SUB CreateRegKeyValue(szKey$, szValue$) STATIC
    DIM phKey AS LONG

    IF RegSetValue(HKEY_CLASSES_ROOT, szKey$, REG_SZ,  szValue$, len(szKey$)) > ERROR_SUCCESS THEN
        i% = EercErrorHandler(GRC_API_FAILED, 1, "CreateRegKeyValue", NULL, NULL)
'$ifdef DEBUG
        StfApiErr saeFail, "CreateRegKeyValue", szKey$+", "+szValue$
'$endif ''DEBUG
        ERROR STFERR
    END IF
END SUB


'**************************************************************************
FUNCTION DoesRegKeyExist(szKey$) STATIC AS INTEGER
    DIM phKey AS LONG

    IF RegOpenKey(HKEY_CLASSES_ROOT, szKey$, VARPTR(phKey)) = ERROR_SUCCESS THEN
        i = RegCloseKey(phKey)
        DoesRegKeyExist = 1
    ELSE
        DoesRegKeyExist = 0
    ENDIF
END FUNCTION


'**************************************************************************
SUB SetRegKeyValue(szKey$, szValue$) STATIC
    DIM phKey AS LONG

    IF RegSetValue(HKEY_CLASSES_ROOT, szKey$, REG_SZ,  szValue$, len(szKey$)) > ERROR_SUCCESS THEN
        i% = EercErrorHandler(GRC_API_FAILED, 1, "SetRegKeyValue", NULL, NULL)
'$ifdef DEBUG
        StfApiErr saeFail, "SetRegKeyValue", szKey$+", "+szValue$
'$endif ''DEBUG
        ERROR STFERR
    END IF
END SUB


'**************************************************************************
FUNCTION GetRegKeyValue(szKey$) STATIC AS STRING
    szValue$ = string$(512,32)
    cb& = len(szValue$)

    IF DoesRegKeyExist(szKey$) = 0 THEN
        GetRegKeyValue = ""
        EXIT FUNCTION
    END IF

    IF RegQueryValue(HKEY_CLASSES_ROOT, szKey$, szValue$, VARPTR(cb)) = ERROR_SUCCESS THEN
        GetRegKeyValue = MID$(szValue$, 1, cb)
    ELSE
        i% = EercErrorHandler(GRC_API_FAILED, 1, "SetRegKeyValue", NULL, NULL)
'$ifdef DEBUG
        StfApiErr saeFail, "GetRegKeyValue", szKey$
'$endif ''DEBUG
        ERROR STFERR
    END IF
  szValue$ = ""
END FUNCTION


'**************************************************************************
SUB DeleteRegKey(szKey$) STATIC
    i& = RegDeleteKey(HKEY_CLASSES_ROOT, szKey$)
END SUB

