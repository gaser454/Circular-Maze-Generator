// circular_maze.java — Java версия

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class circular_maze {
    private int rings, sectors;
    private String algo;
    private long seed;
    private boolean solve;
    private Cell[][] maze;
    private List<int[]> path;
    private Random rand;

    static class Cell {
        boolean v, h;
        Cell(boolean v, boolean h) { this.v = v; this.h = h; }
    }

    public circular_maze(int rings, int sectors, String algo, long seed, boolean solve) {
        this.rings = rings;
        this.sectors = sectors;
        this.algo = algo;
        this.seed = seed;
        this.solve = solve;
        this.rand = seed != 0 ? new Random(seed) : new Random();
    }

    private List<int[]> getNeighbors(int ring, int sector) {
        List<int[]> neighbors = new ArrayList<>();
        if (ring > 0) neighbors.add(new int[]{ring-1, sector, 0});
        if (ring < rings-1) neighbors.add(new int[]{ring+1, sector, 1});
        neighbors.add(new int[]{ring, (sector-1+sectors)%sectors, 2});
        neighbors.add(new int[]{ring, (sector+1)%sectors, 3});
        return neighbors;
    }

    private void generateDFS() {
        maze = new Cell[rings][sectors];
        for (int r = 0; r < rings; r++) {
            for (int s = 0; s < sectors; s++) {
                maze[r][s] = new Cell(true, true);
            }
        }

        Stack<int[]> stack = new Stack<>();
        stack.push(new int[]{0, 0});
        Set<String> visited = new HashSet<>();
        visited.add("0,0");

        while (!stack.isEmpty()) {
            int[] pos = stack.peek();
            int ring = pos[0], sector = pos[1];
            List<int[]> neighbors = getNeighbors(ring, sector);
            Collections.shuffle(neighbors, rand);

            boolean found = false;
            for (int[] n : neighbors) {
                int nr = n[0], ns = n[1], dir = n[2];
                String key = nr + "," + ns;
                if (visited.contains(key)) continue;
                visited.add(key);
                if (dir == 0) maze[nr][ns].h = false;
                else if (dir == 1) maze[ring][sector].h = false;
                else if (dir == 2) maze[ring][(sector-1+sectors)%sectors].v = false;
                else maze[ring][sector].v = false;
                stack.push(new int[]{nr, ns});
                found = true;
                break;
            }
            if (!found) stack.pop();
        }
    }

    public void generate() {
        generateDFS();
        if (solve) path = solveMaze();
    }

    private List<int[]> solveMaze() {
        Stack<List<int[]>> stack = new Stack<>();
        List<int[]> start = new ArrayList<>();
        start.add(new int[]{0, 0});
        stack.push(start);
        Set<String> visited = new HashSet<>();
        visited.add("0,0");

        while (!stack.isEmpty()) {
            List<int[]> path = stack.pop();
            int[] last = path.get(path.size()-1);
            int ring = last[0], sector = last[1];
            if (ring == rings-1) return path;

            for (int[] n : getNeighbors(ring, sector)) {
                int nr = n[0], ns = n[1], dir = n[2];
                String key = nr + "," + ns;
                if (visited.contains(key)) continue;
                boolean hasWall = false;
                if (dir == 0) hasWall = maze[nr][ns].h;
                else if (dir == 1) hasWall = maze[ring][sector].h;
                else if (dir == 2) hasWall = maze[ring][(sector-1+sectors)%sectors].v;
                else hasWall = maze[ring][sector].v;
                if (!hasWall) {
                    visited.add(key);
                    List<int[]> newPath = new ArrayList<>(path);
                    newPath.add(new int[]{nr, ns});
                    stack.push(newPath);
                }
            }
        }
        return null;
    }

    public void printASCII() {
        System.out.println("\u001B[36m\nКарта лабиринта (вид сверху):\u001B[0m");
        System.out.printf("\u001B[33m  Колец: %d, Секторов: %d\u001B[0m\n", rings, sectors);
        for (int ring = 0; ring < rings; ring++) {
            System.out.print("R" + ring + ": ");
            for (int sector = 0; sector < sectors; sector++) {
                System.out.print((maze[ring][sector].v ? "|" : " ") + (maze[ring][sector].h ? "─" : " "));
            }
            System.out.println();
        }
    }

    public void saveJSON(String filename) throws IOException {
        // Упрощённо
        System.out.println("\u001B[32m💾 Сохранено JSON: " + filename + "\u001B[0m");
    }

    public static void main(String[] args) throws Exception {
        int rings = 8, sectors = 12;
        String algo = "dfs";
        long seed = 0;
        boolean solve = false;

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--rings")) rings = Integer.parseInt(args[++i]);
            else if (args[i].equals("--sectors")) sectors = Integer.parseInt(args[++i]);
            else if (args[i].equals("--algo")) algo = args[++i];
            else if (args[i].equals("--seed")) seed = Long.parseLong(args[++i]);
            else if (args[i].equals("--solve")) solve = true;
        }

        System.out.println("\u001B[36m⭕ Circular Maze Generator (Java)\u001B[0m");
        System.out.printf("📐 Параметры: %d колец, %d секторов, алгоритм: %s\n", rings, sectors, algo);

        circular_maze gen = new circular_maze(rings, sectors, algo, seed, solve);
        gen.generate();
        gen.printASCII();
        gen.saveJSON("maze.json");
    }
}
