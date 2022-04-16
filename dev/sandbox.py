#!/usr/bin/env python
# coding: utf-8

# except ブロックでcontine した場合のfinally ブロックの扱いを確認

for i in range(0,5):
    print(i)
    print('open a browser.')
    try:
        if i == 3:
            raise Exception('oops!')
        
    except Exception as e:
        print(e)
        print('should skip the analysis')
        continue
    finally:
        print('close a browser.')
    
    print('analysis.')
        
