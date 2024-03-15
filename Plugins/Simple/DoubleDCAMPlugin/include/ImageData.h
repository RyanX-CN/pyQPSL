#ifndef IMAGEDATA_H
#define IMAGEDATA_H

#include <memory>
#include <cstring>


template <typename PIXELTYPE = unsigned char>
struct ImageData {
    std::unique_ptr<PIXELTYPE[]> m_image_data;
    int width, height;
    ImageData() = default;
    ImageData(PIXELTYPE *bits, int w, int h) {
        m_image_data = std::make_unique<PIXELTYPE[]>(w * h);
        std::memcpy(m_image_data.get(), bits, w * h * sizeof(PIXELTYPE));
        width = w;
        height = h;
    }
    inline PIXELTYPE at(int i, int j) const {
        return *(m_image_data.get() + i * width + j);
    }
};

#endif