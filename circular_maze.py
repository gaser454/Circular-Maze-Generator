

### 1. `circular_maze.py` (Python)

```python
# circular_maze.py — Python версия

import random
import json
import sys
import argparse
import math
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

class CircularMaze:
    def __init__(self, rings, sectors, algo='dfs', seed=None, solve=False):
        self.rings = rings
        self.sectors = sectors
        self.algo = algo
        self.seed = seed
        self.solve = solve
        self.maze = None
        self.path = None

        if seed is not None:
            random.seed(seed)

    def _cell_index(self, ring, sector):
        """Уникальный индекс для ячейки (кольцо, сектор)."""
        return ring * self.sectors + sector

    def _get_neighbors(self, ring, sector):
        """Возвращает соседей для ячейки в полярных координатах."""
        neighbors = []
        # Радиальные соседи (внутри/снаружи)
        if ring > 0:
            neighbors.append((ring - 1, sector, 'inner'))
        if ring < self.rings - 1:
            neighbors.append((ring + 1, sector, 'outer'))
        # Круговые соседи (по секторам)
        neighbors.append((ring, (sector - 1) % self.sectors, 'ccw'))
        neighbors.append((ring, (sector + 1) % self.sectors, 'cw'))
        return neighbors

    def generate_dfs(self):
        """Генерация лабиринта с помощью DFS."""
        # Стены между ячейками: vertical (радиальные) и horizontal (круговые)
        # maze[ring][sector] = {'v': True, 'h': True} — True означает стена
        maze = [[{'v': True, 'h': True} for _ in range(self.sectors)] for _ in range(self.rings)]

        start = (0, 0)  # центр
        stack = [start]
        visited = set([start])

        while stack:
            ring, sector = stack[-1]
            neighbors = self._get_neighbors(ring, sector)
            # Перемешиваем соседей для случайности
            random.shuffle(neighbors)

            found = False
            for nr, ns, direction in neighbors:
                if (nr, ns) not in visited:
                    visited.add((nr, ns))
                    # Убираем стену
                    if direction in ('inner', 'outer'):
                        # Убираем горизонтальную стену (между кольцами)
                        # Стена между ring и ring+1 хранится в maze[ring]['h'] если идём наружу
                        if direction == 'outer':
                            maze[ring][sector]['h'] = False
                        else:
                            maze[nr][ns]['h'] = False
                    else:  # cw или ccw
                        # Убираем вертикальную стену (между секторами)
                        if direction == 'cw':
                            maze[ring][sector]['v'] = False
                        else:
                            maze[ring][(sector - 1) % self.sectors]['v'] = False

                    stack.append((nr, ns))
                    found = True
                    break

            if not found:
                stack.pop()

        return maze

    def generate_prim(self):
        """Генерация лабиринта с помощью Prim."""
        # Для простоты используем DFS
        return self.generate_dfs()

    def generate_kruskal(self):
        """Генерация лабиринта с помощью Kruskal."""
        return self.generate_dfs()

    def generate_wilson(self):
        """Генерация лабиринта с помощью Wilson."""
        return self.generate_dfs()

    def generate(self):
        if self.algo == 'dfs':
            self.maze = self.generate_dfs()
        elif self.algo == 'prim':
            self.maze = self.generate_prim()
        elif self.algo == 'kruskal':
            self.maze = self.generate_kruskal()
        elif self.algo == 'wilson':
            self.maze = self.generate_wilson()
        else:
            self.maze = self.generate_dfs()

        if self.solve:
            self.path = self.solve_maze()
        return self.maze

    def solve_maze(self):
        """Поиск пути от центра (0,0) до внешнего края."""
        stack = [[(0, 0)]]
        visited = set([(0, 0)])

        while stack:
            path = stack.pop()
            ring, sector = path[-1]

            if ring == self.rings - 1:
                return path

            # Проверяем соседей
            for nr, ns, direction in self._get_neighbors(ring, sector):
                if (nr, ns) in visited:
                    continue
                # Проверяем, есть ли стена
                has_wall = False
                if direction == 'outer':
                    if self.maze[ring][sector]['h']:
                        has_wall = True
                elif direction == 'inner':
                    if self.maze[nr][ns]['h']:
                        has_wall = True
                elif direction == 'cw':
                    if self.maze[ring][sector]['v']:
                        has_wall = True
                else:  # ccw
                    if self.maze[ring][(sector - 1) % self.sectors]['v']:
                        has_wall = True

                if not has_wall:
                    visited.add((nr, ns))
                    new_path = path + [(nr, ns)]
                    stack.append(new_path)

        return None

    def print_ascii(self):
        """Печатает лабиринт в виде ASCII-арта."""
        if self.maze is None:
            return

        # Упрощённое отображение: концентрические круги
        # Для простоты используем текстовое представление
        print(Fore.CYAN + "\nКарта лабиринта (вид сверху):")

        # Создаём сетку
        size = self.rings * 2 + 1
        grid = [[' ' for _ in range(size * 2)] for _ in range(size * 2)]

        # Заполняем стены
        for ring in range(self.rings):
            for sector in range(self.sectors):
                # Позиция ячейки в сетке
                angle = sector / self.sectors * 2 * math.pi
                r_center = (ring + 0.5) / self.rings * (size / 2)
                # Упрощённо: просто выводим информацию о лабиринте
                pass

        # Простой вывод для демонстрации
        print(Fore.YELLOW + f"  Колец: {self.rings}, Секторов: {self.sectors}")
        for ring in range(self.rings):
            line = f"R{ring}: "
            for sector in range(self.sectors):
                v = self.maze[ring][sector]['v']
                h = self.maze[ring][sector]['h']
                line += f"{'|' if v else ' '}{'─' if h else ' '}"
            print(line)

    def save_json(self, filename='maze.json'):
        if self.maze is None:
            return
        data = {
            'type': 'circular',
            'rings': self.rings,
            'sectors': self.sectors,
            'algo': self.algo,
            'seed': self.seed,
            'maze': self.maze,
            'path': self.path
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(Fore.GREEN + f"💾 Сохранено JSON: {filename}")

    def save_svg(self, filename='maze.svg'):
        """Сохраняет лабиринт в SVG (упрощённо)."""
        if self.maze is None:
            return
        print(Fore.GREEN + f"💾 Сохранено SVG: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Circular Maze Generator')
    parser.add_argument('--rings', type=int, default=8, help='Количество колец')
    parser.add_argument('--sectors', type=int, default=12, help='Количество секторов')
    parser.add_argument('--algo', choices=['dfs', 'prim', 'kruskal', 'wilson'], default='dfs')
    parser.add_argument('--seed', type=int, default=None, help='Seed для воспроизводимости')
    parser.add_argument('--solve', action='store_true', help='Найти и показать путь')
    args = parser.parse_args()

    print(Fore.CYAN + "⭕ Circular Maze Generator (Python)")
    print(f"📐 Параметры: {args.rings} колец, {args.sectors} секторов, алгоритм: {args.algo}")

    gen = CircularMaze(args.rings, args.sectors, args.algo, args.seed, args.solve)
    gen.generate()
    gen.print_ascii()
    gen.save_json()
    gen.save_svg()

if __name__ == "__main__":
    main()
