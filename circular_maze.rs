// circular_maze.rs — Rust версия

use rand::Rng;
use rand::SeedableRng;
use rand::rngs::StdRng;
use std::collections::{HashSet, VecDeque};
use std::env;

#[derive(Clone, Debug)]
struct Cell {
    v: bool,
    h: bool,
}

struct CircularMaze {
    rings: usize,
    sectors: usize,
    algo: String,
    seed: u64,
    solve: bool,
    maze: Vec<Vec<Cell>>,
    path: Option<Vec<(usize, usize)>>,
    rng: StdRng,
}

impl CircularMaze {
    fn new(rings: usize, sectors: usize, algo: String, seed: u64, solve: bool) -> Self {
        let rng = if seed != 0 {
            StdRng::seed_from_u64(seed)
        } else {
            StdRng::from_entropy()
        };
        CircularMaze {
            rings,
            sectors,
            algo,
            seed,
            solve,
            maze: Vec::new(),
            path: None,
            rng,
        }
    }

    fn get_neighbors(&self, ring: usize, sector: usize) -> Vec<(usize, usize, i32)> {
        let mut neighbors = Vec::new();
        if ring > 0 {
            neighbors.push((ring - 1, sector, 0));
        }
        if ring < self.rings - 1 {
            neighbors.push((ring + 1, sector, 1));
        }
        neighbors.push((ring, (sector + self.sectors - 1) % self.sectors, 2));
        neighbors.push((ring, (sector + 1) % self.sectors, 3));
        neighbors
    }

    fn generate_dfs(&mut self) {
        let mut maze = vec![vec![Cell { v: true, h: true }; self.sectors]; self.rings];

        let mut stack = vec![(0, 0)];
        let mut visited = HashSet::new();
        visited.insert((0, 0));

        while let Some(&(ring, sector)) = stack.last() {
            let mut neighbors = self.get_neighbors(ring, sector);
            // Shuffle
            let len = neighbors.len();
            for i in 0..len {
                let j = self.rng.gen_range(0..len);
                neighbors.swap(i, j);
            }

            let mut found = false;
            for &(nr, ns, dir) in &neighbors {
                if visited.contains(&(nr, ns)) {
                    continue;
                }
                visited.insert((nr, ns));
                match dir {
                    0 => maze[nr][ns].h = false,
                    1 => maze[ring][sector].h = false,
                    2 => maze[ring][(sector + self.sectors - 1) % self.sectors].v = false,
                    3 => maze[ring][sector].v = false,
                    _ => {}
                }
                stack.push((nr, ns));
                found = true;
                break;
            }
            if !found {
                stack.pop();
            }
        }
        self.maze = maze;
    }

    fn generate(&mut self) {
        self.generate_dfs();
        if self.solve {
            self.path = self.solve_maze();
        }
    }

    fn solve_maze(&self) -> Option<Vec<(usize, usize)>> {
        let mut stack = vec![vec![(0, 0)]];
        let mut visited = HashSet::new();
        visited.insert((0, 0));

        while let Some(path) = stack.pop() {
            let &(ring, sector) = path.last().unwrap();
            if ring == self.rings - 1 {
                return Some(path);
            }

            for (nr, ns, dir) in self.get_neighbors(ring, sector) {
                if visited.contains(&(nr, ns)) {
                    continue;
                }
                let has_wall = match dir {
                    0 => self.maze[nr][ns].h,
                    1 => self.maze[ring][sector].h,
                    2 => self.maze[ring][(sector + self.sectors - 1) % self.sectors].v,
                    3 => self.maze[ring][sector].v,
                    _ => true,
                };
                if !has_wall {
                    visited.insert((nr, ns));
                    let mut new_path = path.clone();
                    new_path.push((nr, ns));
                    stack.push(new_path);
                }
            }
        }
        None
    }

    fn print_ascii(&self) {
        println!("\x1b[36m\nКарта лабиринта (вид сверху):\x1b[0m");
        println!("\x1b[33m  Колец: {}, Секторов: {}\x1b[0m", self.rings, self.sectors);
        for ring in 0..self.rings {
            print!("R{}: ", ring);
            for sector in 0..self.sectors {
                let v = if self.maze[ring][sector].v { "|" } else { " " };
                let h = if self.maze[ring][sector].h { "─" } else { " " };
                print!("{}{}", v, h);
            }
            println!();
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut rings = 8;
    let mut sectors = 12;
    let mut algo = "dfs".to_string();
    let mut seed = 0;
    let mut solve = false;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "--rings" => { rings = args[i+1].parse().unwrap_or(8); i += 2; }
            "--sectors" => { sectors = args[i+1].parse().unwrap_or(12); i += 2; }
            "--algo" => { algo = args[i+1].clone(); i += 2; }
            "--seed" => { seed = args[i+1].parse().unwrap_or(0); i += 2; }
            "--solve" => { solve = true; i += 1; }
            _ => { i += 1; }
        }
    }

    println!("\x1b[36m⭕ Circular Maze Generator (Rust)\x1b[0m");
    println!("📐 Параметры: {} колец, {} секторов, алгоритм: {}", rings, sectors, algo);

    let mut gen = CircularMaze::new(rings, sectors, algo, seed, solve);
    gen.generate();
    gen.print_ascii();
}
