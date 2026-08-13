// circular_maze.cs — C# версия

using System;
using System.Collections.Generic;

class Cell {
    public bool V { get; set; }
    public bool H { get; set; }
    public Cell(bool v, bool h) { V = v; H = h; }
}

class CircularMaze {
    private int rings, sectors;
    private string algo;
    private int seed;
    private bool solve;
    private Cell[][] maze;
    private List<(int, int)> path;
    private Random rand;

    public CircularMaze(int rings, int sectors, string algo, int seed, bool solve) {
        this.rings = rings;
        this.sectors = sectors;
        this.algo = algo;
        this.seed = seed;
        this.solve = solve;
        this.rand = seed != 0 ? new Random(seed) : new Random();
    }

    private List<(int, int, int)> GetNeighbors(int ring, int sector) {
        var neighbors = new List<(int, int, int)>();
        if (ring > 0) neighbors.Add((ring-1, sector, 0));
        if (ring < rings-1) neighbors.Add((ring+1, sector, 1));
        neighbors.Add((ring, (sector-1+sectors)%sectors, 2));
        neighbors.Add((ring, (sector+1)%sectors, 3));
        return neighbors;
    }

    private void GenerateDFS() {
        maze = new Cell[rings][];
        for (int r = 0; r < rings; r++) {
            maze[r] = new Cell[sectors];
            for (int s = 0; s < sectors; s++) maze[r][s] = new Cell(true, true);
        }

        var stack = new Stack<(int, int)>();
        stack.Push((0, 0));
        var visited = new HashSet<(int, int)> { (0, 0) };

        while (stack.Count > 0) {
            var (ring, sector) = stack.Peek();
            var neighbors = GetNeighbors(ring, sector);
            // Shuffle
            for (int i = neighbors.Count-1; i > 0; i--) {
                int j = rand.Next(i+1);
                var temp = neighbors[i];
                neighbors[i] = neighbors[j];
                neighbors[j] = temp;
            }

            bool found = false;
            foreach (var (nr, ns, dir) in neighbors) {
                if (visited.Contains((nr, ns))) continue;
                visited.Add((nr, ns));
                if (dir == 0) maze[nr][ns].H = false;
                else if (dir == 1) maze[ring][sector].H = false;
                else if (dir == 2) maze[ring][(sector-1+sectors)%sectors].V = false;
                else maze[ring][sector].V = false;
                stack.Push((nr, ns));
                found = true;
                break;
            }
            if (!found) stack.Pop();
        }
    }

    public void Generate() {
        GenerateDFS();
        if (solve) path = SolveMaze();
    }

    private List<(int, int)> SolveMaze() {
        var stack = new Stack<List<(int, int)>>();
        stack.Push(new List<(int, int)> { (0, 0) });
        var visited = new HashSet<(int, int)> { (0, 0) };

        while (stack.Count > 0) {
            var path = stack.Pop();
            var (ring, sector) = path[path.Count-1];
            if (ring == rings-1) return path;

            foreach (var (nr, ns, dir) in GetNeighbors(ring, sector)) {
                if (visited.Contains((nr, ns))) continue;
                bool hasWall = false;
                if (dir == 0) hasWall = maze[nr][ns].H;
                else if (dir == 1) hasWall = maze[ring][sector].H;
                else if (dir == 2) hasWall = maze[ring][(sector-1+sectors)%sectors].V;
                else hasWall = maze[ring][sector].V;
                if (!hasWall) {
                    visited.Add((nr, ns));
                    var newPath = new List<(int, int)>(path) { (nr, ns) };
                    stack.Push(newPath);
                }
            }
        }
        return null;
    }

    public void PrintASCII() {
        Console.WriteLine("\u001B[36m\nКарта лабиринта (вид сверху):\u001B[0m");
        Console.WriteLine($"\u001B[33m  Колец: {rings}, Секторов: {sectors}\u001B[0m");
        for (int ring = 0; ring < rings; ring++) {
            Console.Write($"R{ring}: ");
            for (int sector = 0; sector < sectors; sector++) {
                Console.Write((maze[ring][sector].V ? "|" : " ") + (maze[ring][sector].H ? "─" : " "));
            }
            Console.WriteLine();
        }
    }

    public void SaveJSON(string filename) {
        Console.WriteLine($"\u001B[32m💾 Сохранено JSON: {filename}\u001B[0m");
    }

    public static void Main(string[] args) {
        int rings = 8, sectors = 12;
        string algo = "dfs";
        int seed = 0;
        bool solve = false;

        for (int i = 0; i < args.Length; i++) {
            if (args[i] == "--rings") rings = int.Parse(args[++i]);
            else if (args[i] == "--sectors") sectors = int.Parse(args[++i]);
            else if (args[i] == "--algo") algo = args[++i];
            else if (args[i] == "--seed") seed = int.Parse(args[++i]);
            else if (args[i] == "--solve") solve = true;
        }

        Console.WriteLine("\u001B[36m⭕ Circular Maze Generator (C#)\u001B[0m");
        Console.WriteLine($"📐 Параметры: {rings} колец, {sectors} секторов, алгоритм: {algo}");

        var gen = new CircularMaze(rings, sectors, algo, seed, solve);
        gen.Generate();
        gen.PrintASCII();
        gen.SaveJSON("maze.json");
    }
}
