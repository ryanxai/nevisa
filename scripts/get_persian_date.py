#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to get today's date in Persian (Jalali) calendar format.
Used by LaTeX preamble.tex via shell escape.
Outputs a LaTeX command definition that can be \\input.
"""
import sys

try:
    from khayyam import JalaliDatetime
    
    # Get today's date in Persian calendar
    today = JalaliDatetime.now()
    
    # Format: Persian date with month name (e.g., "۲ دی ۱۴۰۴")
    # Using strftime format directives for Persian calendar
    # %d = day, %B = full month name, %Y = year
    persian_date = today.strftime('%d %B %Y')
    
    # Convert English numerals to Persian numerals
    persian_digits = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    # Replace each English digit with Persian digit
    persian_date_converted = ''.join(persian_digits.get(char, char) for char in persian_date)
    
    # Output LaTeX command definition
    # Escape any special LaTeX characters in the date
    persian_date_escaped = persian_date_converted.replace('\\', '\\textbackslash{}').replace('{', '\\{').replace('}', '\\}')
    print(f'\\def\\jalalidate{{{persian_date_escaped}}}')
except ImportError:
    # Fallback if khayyam is not installed - output to stdout so LaTeX can use it
    print('\\def\\jalalidate{تاریخ نامشخص}')
except Exception as e:
    # Fallback on any error - output to stdout so LaTeX can use it
    print('\\def\\jalalidate{تاریخ نامشخص}')

