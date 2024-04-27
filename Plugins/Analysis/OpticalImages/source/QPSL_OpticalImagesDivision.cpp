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
    static constexpr int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
    struct ImageDivisor {
        int m_width, m_height, m_down_ratio, m_down_width, m_down_height, m_binary_th, m_radius;
        unsigned short *m_buffer;
        unsigned short *m_down_buffer;
        bool *m_mask;
        unsigned short at(int i, int j) {
            if (i < m_height && j < m_width)
                return m_buffer[i * m_width + j];
            else {
                return 0;
            }
        }
        void get_down_buffer() {
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
        void get_real_mask(const std::vector<bool> &down_mask) {
            struct node {
                int i, j, dis;
            };
            std::queue<node> Q;
            for (int i = 0; i < m_down_height; i++)
                for (int j = 0; j < m_down_width; j++)
                    if (down_mask[i * m_down_width + j]) {
                        for (int ii = i * m_down_ratio, iend = (i + 1) * m_down_ratio; ii < iend; ii++)
                            for (int jj = j * m_down_ratio, jend = (j + 1) * m_down_ratio; jj < jend; jj++)
                                if (ii < m_height && jj < m_width) {
                                    Q.push({ii, jj, 0});
                                    m_mask[ii * m_width + jj] = true;
                                }
                    } else {
                        for (int ii = i * m_down_ratio, iend = (i + 1) * m_down_ratio; ii < iend; ii++)
                            for (int jj = j * m_down_ratio, jend = (j + 1) * m_down_ratio; jj < jend; jj++)
                                if (ii < m_height && jj < m_width) {
                                    m_mask[ii * m_width + jj] = false;
                                }
                    }
            while (Q.size()) {
                auto [i, j, dis] = Q.front();
                Q.pop();
                if (dis >= m_down_ratio) continue;
                for (int k = 0; k < 4; k++) {
                    int ii = i + dirs[k][0], jj = j + dirs[k][1];
                    if (ii >= 0 && ii < m_height && jj >= 0 && jj < m_width && !m_mask[ii * m_width + jj]) {
                        m_mask[ii * m_width + jj] = true;
                        Q.push({ii, jj, dis + 1});
                    }
                }
            }
        }
        std::vector<bool> get_down_mask() {
            struct node {
                int i, j;
            };
            const int n = m_down_height * m_down_width;
            std::vector<int> v_find(n), v_size(n, 1), distance(n, INT_MAX / 2);
            std::vector<bool> isblack(n);
            std::queue<node> Q;
            int max_group_size = 0;
            for (int i = 0; i < n; i++) v_find[i] = i;
            auto find = [&](auto self, int i) {
                if (v_find[i] == i)
                    return i;
                else
                    return v_find[i] = self(self, v_find[i]);
            };
            auto merge = [&](int i, int j) {
                i = find(find, i), j = find(find, j);
                if (i != j) {
                    v_size[i] += v_size[j];
                    v_find[j] = i;
                    max_group_size = std::max(max_group_size, v_size[i]);
                }
            };
            auto size = [&](int i, int j) {
                return v_size[find(find, i * m_down_width + j)];
            };
            for (int i = 0; i < m_down_height; i++) {
                for (int j = 0; j < m_down_width; j++) {
                    if (m_down_buffer[i * m_down_width + j] >= m_binary_th) {
                        for (int k = 0; k < 4; k++) {
                            int ii = i + dirs[k][0], jj = j + dirs[k][1];
                            if (ii >= 0 && ii < m_down_height && jj >= 0 && jj < m_down_width && m_down_buffer[ii * m_down_width + jj] >= m_binary_th) {
                                merge(i * m_down_width + j, ii * m_down_width + jj);
                            }
                        }
                    }
                }
            }
            for (int i = 0; i < m_down_height; i++) {
                for (int j = 0; j < m_down_width; j++) {
                    if (size(i, j) == max_group_size) {
                        isblack[i * m_down_width + j] = true;
                        distance[i * m_down_width + j] = 0;
                        Q.push({i, j});
                    }
                }
            }
            while (Q.size()) {
                auto [i, j] = Q.front();
                Q.pop();
                if (distance[i * m_down_width + j] >= m_radius) continue;
                for (int k = 0; k < 4; k++) {
                    int ii = i + dirs[k][0], jj = j + dirs[k][1];
                    if (ii >= 0 && ii < m_down_height && jj >= 0 && jj < m_down_width && distance[ii * m_down_width + jj] > distance[i * m_down_width + j] + 1) {
                        distance[ii * m_down_width + jj] = distance[i * m_down_width + j] + 1;
                        isblack[ii * m_down_width + jj] = true;
                        Q.push({ii, jj});
                    }
                }
            }
            return isblack;
        }
        void run() {
            get_down_buffer();
            auto down_mask = get_down_mask();
            get_real_mask(down_mask);
        }
    };
    void get_edge_by_mask(bool *edge_arr, bool *mask, int m_height, int m_width, int point_size) {
        struct node {
            int i, j;
        };
        std::queue<node> Q;
        for (int j = 0; j < m_width; j++)
            if (!mask[j]) {
                edge_arr[j] = true;
                Q.push({0, j});
            }
        for (int i = 1; i + 1 < m_height; i++) {
            if (!mask[i * m_width]) {
                edge_arr[i * m_width] = true;
                Q.push({i, 0});
            }
            if (m_width > 1 && !mask[i * m_width + (m_width - 1)]) {
                edge_arr[i * m_width + (m_width - 1)] = true;
                Q.push({i, m_width - 1});
            }
        }
        for (int j = 0; j < m_width; j++)
            if (!mask[m_width * (m_height - 1) + j]) {
                edge_arr[m_width * (m_height - 1) + j] = true;
                Q.push({m_height - 1, j});
            }
        while (Q.size()) {
            auto [i, j] = Q.front();
            Q.pop();
            for (int k = 0; k < 4; k++) {
                int ii = i + dirs[k][0], jj = j + dirs[k][1];
                if (ii >= 0 && ii < m_height && jj >= 0 && jj < m_width && !mask[ii * m_width + jj] && !edge_arr[ii * m_width + jj]) {
                    edge_arr[ii * m_width + jj] = true;
                    Q.push({ii, jj});
                }
            }
        }
        for (int i = 0; i < m_height; i++) {
            for (int j = 0; j < m_width; j++) {
                if (edge_arr[i * m_width + j]) {
                    bool flag = false;
                    for (int k = 0; k < 4; k++) {
                        int ii = i + dirs[k][0], jj = j + dirs[k][1];
                        if (ii >= 0 && ii < m_height && jj >= 0 && jj < m_width && mask[ii * m_width + jj]) {
                            flag = true;
                            break;
                        }
                    }
                    edge_arr[i * m_width + j] = flag;
                    if (flag) Q.push({i, j});
                }
            }
        }
        for (int t = 0; t < point_size; t++) {
            int len = Q.size();
            while (len--) {
                auto [i, j] = Q.front();
                Q.pop();
                for (int k = 0; k < 4; k++) {
                    int ii = i + dirs[k][0], jj = j + dirs[k][1];
                    if (ii >= 0 && ii < m_height && jj >= 0 && jj < m_width && !edge_arr[ii * m_width + jj]) {
                        edge_arr[ii * m_width + jj] = true;
                        Q.push({ii, jj});
                    }
                }
            }
        }
    }
}

#ifdef __cplusplus
extern "C" {
#endif
#define DLL_EXPORT __declspec(dllexport)

void DLL_EXPORT QPSL_Divisor_run(OY::ImageDivisor *ptr) {
    ptr->run();
}
void DLL_EXPORT QPSL_Divisor_get_edge_by_mask(bool *edge_arr, bool *mask, int height, int width, int point_size) {
    OY::get_edge_by_mask(edge_arr, mask, height, width, point_size);
}

#ifdef __cplusplus
}
#endif
#endif

/*
g++ divide.cpp -o ../bin/image_division.dll -shared -fPIC -O3
*/
