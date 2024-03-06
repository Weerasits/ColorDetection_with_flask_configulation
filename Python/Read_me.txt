วิธีการใช้งานกล้อง ColorDetection + WebServer

1. แก้ Source code เพื่อใช้งาน

1.1 PLC Connection

===============================================
- colordetection.py

Line
18    plc_address = '192.168.250.1'   // Ip Address ของ PLC
19    plc_last_address = 1  // เลขตัวสุดท้ายของ Address PLC
20    server_last_address = 66 // เลขตัวสุดท้ายของ PC 
===============================================


1.2 Webserver Address
 
===============================================
- server.py

Line
277   app.run(host='192.168.250.66') // แก้เลขข้างใน host='____' เป็น ip ตัวที่รัน Python

===============================================


2. Run Python

โปรแกรมกล้อง Colordetection + PLC Connection ชื่อไฟล์ว่า colordetection.py

โปรแกรมดึงกล้องไปแสดงผลบนเว็บ ชื่อไฟล์ว่า server.py

สองตัวนี้แยกกันทำงาน ถ้าไม่รัน server.py ตัวกล้องก็ยังสามารถทำงานร่วมกับ PLC ได้

ถ้าอยากทำงาน Full option ต้องรันทั้งสองตัวพร้อมกันนะครับผม


Credit : Weerasit Surinarporn : SCG Excellence model school 

Date : 8/2/2024



หากเปิดไฟล์นี้ในปี 2028 ผมน่าจะเรียน ปตรีจบแล้ว หาก Nawaplastic หาวิศวกรไม่ได้ โทร 0880040098

ขอบคุณครับ <3