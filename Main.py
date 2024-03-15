from Tool import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QPSLMainWindow()
    main_window.show()
    sys.exit(app.exec())

# import pyqtgraph.examples
# pyqtgraph.examples.run()

# x = c_int32(123)
# y =pointer(x).contents
# print(ctypes.addressof(x),ctypes.addressof(y))

# print(bin(2263196295232))
# print(bin(-251469760))

# s=134217728
# z=[]
# for i in range(2, 20000):
#     while s%i==0:
#         z.append(i)
#         s//=i
# z.append(s)
# print(z)

# class ImageData(Structure):
#     _fields_ = [('buffer',str[0] * 33554432),
#                 ('frame_id',int)]  


# imagedata_cam: ImageData    
# framebuffer_cam = np.frombuffer(imagedata_cam.buffer, dtype=np.uint16, count=1<<22)

# print(bin(2269947891776))
# print(bin(3122944573504))

# print(b'e'.decode('utf-8'))
# print(bin(int.from_bytes(b'a','big')))

