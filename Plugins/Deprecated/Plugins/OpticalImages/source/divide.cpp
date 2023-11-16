#ifndef __QPSL_IMAGE3DDIVISION__
#define __QPSL_IMAGE3DDIVISION__

#include <algorithm>
#include <array>
#include <bit>
#include <bitset>
#include <cassert>
#include <climits>
#include <cstring>
#include <fstream>
#include <iostream>
#include <list>
#include <map>
#include <memory>
#include <queue>
#include <random>
#include <set>
#include <sstream>
#include <stack>
#include <unordered_set>
using std::cin, std::endl, std::cout;

namespace OY {
    struct ImageDivisor {
        int m_width, m_height, m_down_ratio, m_down_width, m_down_height, m_binary_th, m_radius;
        unsigned short m_buffer[100000000];
        unsigned short m_down_buffer[100000000];
        unsigned short at(int __i, int __j) {
            if (__i < m_height && __j < m_width)
                return m_buffer[__i * m_width + __j];
            else {
                return 0;
            }
        }
        void get_down_buffer() {
            m_down_height = (m_height + m_down_ratio - 1) / m_down_ratio;
            m_down_width = (m_width + m_down_ratio - 1) / m_down_ratio;
            uint64_t square = m_down_ratio * m_down_ratio;
            int cursor = 0;
            for (int i = 0; i < m_down_height; i++) {
                for (int j = 0; j < m_down_width; j++) {
                    uint64_t sum = 0;
                    for (int ii = i * m_down_ratio, iend = (i + 1) * m_down_ratio; ii < iend; ii++) {
                        for (int jj = j * m_down_ratio, jend = (j + 1) * m_down_ratio; jj < jend; jj++) {
                            sum += at(ii, jj);
                        }
                    }
                    m_down_buffer[cursor++] = sum / square;
                }
            }
        }
        void get_real_mask(const std::vector<bool> &__mask) {
            for (int i = 0; i < m_down_height; i++)
                for (int j = 0; j < m_down_width; j++)
                    if (!__mask[i * m_down_width + j])
                        for (int ii = i * m_down_ratio, iend = (i + 1) * m_down_ratio; ii < iend; ii++)
                            for (int jj = j * m_down_ratio, jend = (j + 1) * m_down_ratio; jj < jend; jj++)
                                if (ii < m_height && jj < m_width) {
                                    m_buffer[ii * m_width + jj] = 0;
                                }
        }
        std::vector<bool> get_down_mask() {
            const int n = m_down_height * m_down_width;
            std::pair<std::vector<int>, std::vector<int>> res;
            int max_group_size = 0;
            res.first.resize(n);
            res.second.resize(n);
            for (int i = 0; i < n; i++) res.first[i] = i, res.second[i] = 1;
            auto find = [&](auto self, int i) {
                if (res.first[i] == i)
                    return i;
                else
                    return res.first[i] = self(self, res.first[i]);
            };
            auto merge = [&](int i, int j) {
                i = find(find, i), j = find(find, j);
                if (i != j) {
                    res.second[i] += res.second[j];
                    res.first[j] = i;
                    max_group_size = std::max(max_group_size, res.second[i]);
                }
            };
            auto size = [&](int i, int j) {
                return res.second[find(find, i * m_down_width + j)];
            };
            for (int i = 0; i < m_down_height; i++) {
                for (int j = 0; j < m_down_width; j++) {
                    if (m_down_buffer[i * m_down_width + j] >= m_binary_th) {
                        for (auto [ii, jj] : std::array<std::array<int, 2>, 4>{{{i + 1, j}, {i, j + 1}, {i - 1, j}, {i, j - 1}}}) {
                            if (ii >= 0 && ii < m_down_height && jj >= 0 && jj < m_down_width && m_down_buffer[ii * m_down_width + jj] >= m_binary_th) {
                                merge(i * m_down_width + j, ii * m_down_width + jj);
                            }
                        }
                    }
                }
            }
            std::vector<int> distance(n, INT_MAX / 2);
            std::vector<bool> isblack(n);
            std::queue<int> Q;
            for (int i = 0; i < m_down_height; i++) {
                for (int j = 0; j < m_down_width; j++) {
                    if (size(i, j) == max_group_size) {
                        isblack[i * m_down_width + j] = true;
                        distance[i * m_down_width + j] = 0;
                        Q.push(i * m_down_width + j);
                    }
                }
            }
            while (Q.size()) {
                auto p = Q.front();
                Q.pop();
                if (distance[p] >= m_radius) continue;
                int i = p / m_down_width, j = p % m_down_width;
                for (auto [ii, jj] : std::array<std::array<int, 2>, 4>{{{i + 1, j}, {i, j + 1}, {i - 1, j}, {i, j - 1}}}) {
                    if (ii >= 0 && ii < m_down_height && jj >= 0 && jj < m_down_width && distance[ii * m_down_width + jj] > distance[p] + 1) {
                        distance[ii * m_down_width + jj] = distance[p] + 1;
                        isblack[ii * m_down_width + jj] = true;
                        Q.push(ii * m_down_width + jj);
                    }
                }
            }
            return isblack;
        }
        void binary_set(uint16_t __th) {
            for (int i = 0; i < m_height; i++) {
                for (int j = 0; j < m_width; j++) {
                    m_buffer[i * m_width + j] = m_buffer[i * m_width + j] >= __th ? 65535 : 0;
                }
            }
        }
        void run() {
            get_down_buffer();
            auto mask = get_down_mask();
            get_real_mask(mask);
        }
    };
}

#ifdef __cplusplus
extern "C" {
#endif
#define DLL_EXPORT __declspec(dllexport)

void DLL_EXPORT QPSL_Divisor_run(OY::ImageDivisor *ptr) {
    ptr->run();
}

#ifdef __cplusplus
}
#endif
#endif

/*
g++ divide.cpp -o image_division.dll -shared -fPIC -O3
*/
