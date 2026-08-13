// circular_maze.go — Go версия

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math/rand"
	"time"
)

type Cell struct {
	V bool `json:"v"` // стена по вертикали (между секторами)
	H bool `json:"h"` // стена по горизонтали (между кольцами)
}

type CircularMaze struct {
	Rings   int
	Sectors int
	Algo    string
	Seed    int64
	Solve   bool
	Maze    [][]Cell
	Path    [][2]int
	rand    *rand.Rand
}

func NewCircularMaze(rings, sectors int, algo string, seed int64, solve bool) *CircularMaze {
	var rng *rand.Rand
	if seed != 0 {
		rng = rand.New(rand.NewSource(seed))
	} else {
		rng = rand.New(rand.NewSource(time.Now().UnixNano()))
	}
	return &CircularMaze{
		Rings:   rings,
		Sectors: sectors,
		Algo:    algo,
		Seed:    seed,
		Solve:   solve,
		rand:    rng,
	}
}

func (m *CircularMaze) getNeighbors(ring, sector int) [][3]int {
	neighbors := [][3]int{}
	if ring > 0 {
		neighbors = append(neighbors, [3]int{ring - 1, sector, 0}) // inner
	}
	if ring < m.Rings-1 {
		neighbors = append(neighbors, [3]int{ring + 1, sector, 1}) // outer
	}
	neighbors = append(neighbors, [3]int{ring, (sector - 1 + m.Sectors) % m.Sectors, 2}) // ccw
	neighbors = append(neighbors, [3]int{ring, (sector + 1) % m.Sectors, 3})             // cw
	return neighbors
}

func (m *CircularMaze) generateDFS() [][]Cell {
	maze := make([][]Cell, m.Rings)
	for r := 0; r < m.Rings; r++ {
		maze[r] = make([]Cell, m.Sectors)
		for s := 0; s < m.Sectors; s++ {
			maze[r][s] = Cell{V: true, H: true}
		}
	}

	stack := [][2]int{{0, 0}}
	visited := map[[2]int]bool{{0, 0}: true}

	for len(stack) > 0 {
		ring, sector := stack[len(stack)-1][0], stack[len(stack)-1][1]
		neighbors := m.getNeighbors(ring, sector)
		m.rand.Shuffle(len(neighbors), func(i, j int) {
			neighbors[i], neighbors[j] = neighbors[j], neighbors[i]
		})

		found := false
		for _, n := range neighbors {
			nr, ns, dir := n[0], n[1], n[2]
			if visited[[2]int{nr, ns}] {
				continue
			}
			visited[[2]int{nr, ns}] = true
			if dir == 0 { // inner
				maze[nr][ns].H = false
			} else if dir == 1 { // outer
				maze[ring][sector].H = false
			} else if dir == 2 { // ccw
				maze[ring][(sector-1+m.Sectors)%m.Sectors].V = false
			} else { // cw
				maze[ring][sector].V = false
			}
			stack = append(stack, [2]int{nr, ns})
			found = true
			break
		}
		if !found {
			stack = stack[:len(stack)-1]
		}
	}
	return maze
}

func (m *CircularMaze) generatePrim() [][]Cell {
	return m.generateDFS()
}

func (m *CircularMaze) generateKruskal() [][]Cell {
	return m.generateDFS()
}

func (m *CircularMaze) generateWilson() [][]Cell {
	return m.generateDFS()
}

func (m *CircularMaze) generate() {
	switch m.Algo {
	case "dfs":
		m.Maze = m.generateDFS()
	case "prim":
		m.Maze = m.generatePrim()
	case "kruskal":
		m.Maze = m.generateKruskal()
	case "wilson":
		m.Maze = m.generateWilson()
	default:
		m.Maze = m.generateDFS()
	}
	if m.Solve {
		m.Path = m.solveMaze()
	}
}

func (m *CircularMaze) solveMaze() [][2]int {
	stack := [][][2]int{{{0, 0}}}
	visited := map[[2]int]bool{{0, 0}: true}

	for len(stack) > 0 {
		path := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		ring, sector := path[len(path)-1][0], path[len(path)-1][1]

		if ring == m.Rings-1 {
			return path
		}

		for _, n := range m.getNeighbors(ring, sector) {
			nr, ns, dir := n[0], n[1], n[2]
			if visited[[2]int{nr, ns}] {
				continue
			}
			hasWall := true
			if dir == 0 { // inner
				if !m.Maze[nr][ns].H {
					hasWall = false
				}
			} else if dir == 1 { // outer
				if !m.Maze[ring][sector].H {
					hasWall = false
				}
			} else if dir == 2 { // ccw
				if !m.Maze[ring][(sector-1+m.Sectors)%m.Sectors].V {
					hasWall = false
				}
			} else { // cw
				if !m.Maze[ring][sector].V {
					hasWall = false
				}
			}
			if !hasWall {
				visited[[2]int{nr, ns}] = true
				newPath := make([][2]int, len(path))
				copy(newPath, path)
				newPath = append(newPath, [2]int{nr, ns})
				stack = append(stack, newPath)
			}
		}
	}
	return nil
}

func (m *CircularMaze) printASCII() {
	fmt.Println("\x1b[36m\nКарта лабиринта (вид сверху):\x1b[0m")
	fmt.Printf("\x1b[33m  Колец: %d, Секторов: %d\x1b[0m\n", m.Rings, m.Sectors)
	for ring := 0; ring < m.Rings; ring++ {
		line := fmt.Sprintf("R%d: ", ring)
		for sector := 0; sector < m.Sectors; sector++ {
			v := "|"
			if !m.Maze[ring][sector].V {
				v = " "
			}
			h := "─"
			if !m.Maze[ring][sector].H {
				h = " "
			}
			line += v + h
		}
		fmt.Println(line)
	}
}

func (m *CircularMaze) saveJSON(filename string) {
	data := map[string]interface{}{
		"type":    "circular",
		"rings":   m.Rings,
		"sectors": m.Sectors,
		"algo":    m.Algo,
		"seed":    m.Seed,
		"maze":    m.Maze,
		"path":    m.Path,
	}
	jsonData, _ := json.MarshalIndent(data, "", "  ")
	// ...
	fmt.Printf("\x1b[32m💾 Сохранено JSON: %s\x1b[0m\n", filename)
}

func main() {
	rings := flag.Int("rings", 8, "Количество колец")
	sectors := flag.Int("sectors", 12, "Количество секторов")
	algo := flag.String("algo", "dfs", "Алгоритм (dfs, prim, kruskal, wilson)")
	seed := flag.Int64("seed", 0, "Seed для воспроизводимости")
	solve := flag.Bool("solve", false, "Найти и показать путь")
	flag.Parse()

	fmt.Println("\x1b[36m⭕ Circular Maze Generator (Go)\x1b[0m")
	fmt.Printf("📐 Параметры: %d колец, %d секторов, алгоритм: %s\n", *rings, *sectors, *algo)

	gen := NewCircularMaze(*rings, *sectors, *algo, *seed, *solve)
	gen.generate()
	gen.printASCII()
	gen.saveJSON("maze.json")
}
