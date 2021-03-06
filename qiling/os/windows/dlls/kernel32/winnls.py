#!/usr/bin/env python3
#
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
# Built on top of Unicorn emulator (www.unicorn-engine.org)

import struct
import time
from qiling.os.windows.const import *
from qiling.os.fncc import *
from qiling.os.windows.fncc import *
from qiling.os.windows.utils import *
from qiling.os.memory import align
from qiling.os.windows.thread import *
from qiling.os.windows.handle import *
from qiling.exception import *


# BOOL SetThreadLocale(
#   LCID Locale
# );
@winapi(cc=STDCALL, params={
    "Locale": UINT
})
def hook_SetThreadLocale(ql, address, params):
    return 0xC000  # LOCALE_CUSTOM_DEFAULT


# UINT GetACP(
# );
@winapi(cc=STDCALL, params={})
def hook_GetACP(ql, address, params):
    return OEM_US


# BOOL GetCPInfo(
#   UINT     CodePage,
#   LPCPINFO lpCPInfo
# );
@winapi(cc=STDCALL, params={
    "CodePage": UINT,
    "lpCPInfo": POINTER
})
def hook_GetCPInfo(ql, address, params):
    ret = 1
    return ret


# int GetLocaleInfoA(
#   LCID   Locale,
#   LCTYPE LCType,
#   LPSTR  lpLCData,
#   int    cchData
# );
@winapi(cc=STDCALL, params={
    "Locale": DWORD,
    "LCType": DWORD,
    "lpLCData": POINTER,
    "cchData": INT,
})
def hook_GetLocaleInfoA(ql, address, params):
    locale_value = params["Locale"]
    lctype_value = params["LCType"]
    cchData = params["cchData"]
    ql.dprint("locale")
    ql.dprint(locale_value)
    ql.dprint("lctype")
    ql.dprint(lctype_value)

    local_dict = LOCALE.get(locale_value, None)
    if local_dict is None:
        raise QlErrorNotImplemented("[!] API not implemented")
    lctype = local_dict[lctype_value] + "\x00"

    if cchData != 0:
        lplcdata = params["lpLCData"]
        ql.uc.mem_write(lplcdata, lctype.encode("utf16-le"))
    return len(lctype)


# BOOL IsValidCodePage(
#  UINT CodePage
# );
@winapi(cc=STDCALL, params={
    "CodePage": UINT
})
def hook_IsValidCodePage(ql, address, params):
    return 1


def _LCMapString(ql, address, params):
    cchDest = params["cchDest"]
    string = params["lpSrcStr"] + "\x00"
    dst = params["lpDestStr"]
    if cchDest != 0:
        # TODO maybe do some other check, for now is working
        ql.uc.mem_write(dst, bytes(string, "utf-16le"))
    return len(string)


# int LCMapStringW(
#   LCID    Locale,
#   DWORD   dwMapFlags,
#   LPCWSTR lpSrcStr,
#   int     cchSrc,
#   LPWSTR  lpDestStr,
#   int     cchDest
# );
@winapi(cc=STDCALL, params={
    "Locale": POINTER,
    "dwMapFlags": DWORD,
    "lpSrcStr": WSTRING,
    "cchSrc": INT,
    "lpDestStr": POINTER,
    "cchDest": INT
})
def hook_LCMapStringW(ql, address, params):
    return _LCMapString(ql, address, params)


# int LCMapStringA(
#   LCID   Locale,
#   DWORD  dwMapFlags,
#   LPCSTR lpSrcStr,
#   int    cchSrc,
#   LPSTR  lpDestStr,
#   int    cchDest
# );
@winapi(cc=STDCALL, params={
    "Locale": POINTER,
    "dwMapFlags": DWORD,
    "lpSrcStr": STRING,
    "cchSrc": INT,
    "lpDestStr": POINTER,
    "cchDest": INT
})
def hook_LCMapStringA(ql, address, params):
    return _LCMapString(ql, address, params)


# int LCMapStringEx(
#   LPCWSTR          lpLocaleName,
#   DWORD            dwMapFlags,
#   LPCWSTR          lpSrcStr,
#   int              cchSrc,
#   LPWSTR           lpDestStr,
#   int              cchDest,
#   LPNLSVERSIONINFO lpVersionInformation,
#   LPVOID           lpReserved,
#   LPARAM           sortHandle
# );
@winapi(cc=STDCALL, params={
    "lpLocaleName": POINTER,
    "dwMapFlags": DWORD,
    "lpSrcStr": WSTRING,
    "cchSrc": INT,
    "lpDestStr": POINTER,
    "cchDest": INT,
    "lpVersionInformation": POINTER,
    "lpReserved": UINT,
    "sortHandle": UINT

})
def hook_LCMapStringEx(ql, address, params):
    return _LCMapString(ql, address, params)
