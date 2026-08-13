// circular_maze.js — JavaScript версия

const fs = require('fs');

class CircularMaze {
    constructor(rings, sectors, algo = 'dfs', seed = null, solve = false) {
        this.rings = rings;
        this.sectors = sectors;
        this.algo = algo;
        this.seed = seed;
        this.solve = solve;
        this.maze = null;
        this.path = null;
        if (seed !== null) {
            this._seedRandom(seed);
        }
    }

    _seedRandom(seed) {
        let s = seed;
        this._rand = () => {
            s = (s * 9301 + 49297) % 233280;
            return s / 233280;
        };
    }

    _rand() {
        return Math.random();
    }

    _getNeighbors(ring, sector) {
        const neighbors = [];
        if (ring > 0) neighbors.push([ring - 1, sector, 'inner']);
        if (ring < this.rings - 1) neighbors.push([ring + 1, sector, 'outer']);
        neighbors.push([ring, (sector - 1 + this.sectors) % this.sectors, 'ccw']);
        neighbors.push([ring, (sector + 1) % this.sectors, 'cw']);
        return neighbors;
    }

    generateDFS() {
        const maze = Array.from({ length: this.rings }, () =>
            Array.from({ length: this.sectors }, () => ({ v: true, h: true }))
        );

        const stack = [[0, 0]];
        const visited = new Set(['0,0']);

        while (stack.length > 0) {
            const [ring, sector] = stack[stack.length - 1];
            const neighbors = this._getNeighbors(ring, sector);
            // Перемешиваем
            for (let i = neighbors.length - 1; i > 0; i--) {
                const j = Math.floor(this._rand() * (i + 1));
                [neighbors[i], neighbors[j]] = [neighbors[j], neighbors[i]];
            }

            let found = false;
            for (const [nr, ns, dir] of neighbors) {
                const key = `${nr},${ns}`;
                if (visited.has(key)) continue;
                visited.add(key);
                if (dir === 'inner') {
                    maze[nr][ns].h = false;
                } else if (dir === 'outer') {
                    maze[ring][sector].h = false;
                } else if (dir === 'ccw') {
                    maze[ring][(sector - 1 + this.sectors) % this.sectors].v = false;
                } else { // cw
                    maze[ring][sector].v = false;
                }
                stack.push([nr, ns]);
                found = true;
                break;
            }
            if (!found) stack.pop();
        }
        return maze;
    }

    generatePrim() { return this.generateDFS(); }
    generateKruskal() { return this.generateDFS(); }
    generateWilson() { return this.generateDFS(); }

    generate() {
        switch (this.algo) {
            case 'dfs': this.maze = this.generateDFS(); break;
            default: this.maze = this.generateDFS();
        }
        if (this.solve) {
            this.path = this.solveMaze();
        }
        return this.maze;
    }

    solveMaze() {
        const stack = [[[0, 0]]];
        const visited = new Set(['0,0']);

        while (stack.length > 0) {
            const path = stack.pop();
            const [ring, sector] = path[path.length - 1];
            if (ring === this.rings - 1) return path;

            for (const [nr, ns, dir] of this._getNeighbors(ring, sector)) {
                const key = `${nr},${ns}`;
                if (visited.has(key)) continue;
                let hasWall = true;
                if (dir === 'inner') hasWall = this.maze[nr][ns].h;
                else if (dir === 'outer') hasWall = this.maze[ring][sector].h;
                else if (dir === 'ccw') hasWall = this.maze[ring][(sector - 1 + this.sectors) % this.sectors].v;
                else hasWall = this.maze[ring][sector].v;
                if (!hasWall) {
                    visited.add(key);
                    const newPath = [...path, [nr, ns]];
                    stack.push(newPath);
                }
            }
        }
        return null;
    }

    printASCII() {
        console.log('\x1b[36m\nКарта лабиринта (вид сверху):\x1b[0m');
        console.log(`\x1b[33m  Колец: ${this.rings}, Секторов: ${this.sectors}\x1b[0m`);
        for (let ring = 0; ring < this.rings; ring++) {
            let line = `R${ring}: `;
            for (let sector = 0; sector < this.sectors; sector++) {
                const v = this.maze[ring][sector].v ? '|' : ' ';
                const h = this.maze[ring][sector].h ? '─' : ' ';
                line += v + h;
            }
            console.log(line);
        }
    }

    saveJSON(filename = 'maze.json') {
        const data = {
            type: 'circular',
            rings: this.rings,
            sectors: this.sectors,
            algo: this.algo,
            seed: this.seed,
            maze: this.maze,
            path: this.path
        };
        fs.writeFileSync(filename, JSON.stringify(data, null, 2));
        console.log(`\x1b[32m💾 Сохранено JSON: ${filename}\x1b[0m`);
    }
}

function main() {
    const args = process.argv.slice(2);
    let rings = 8, sectors = 12, algo = 'dfs', seed = null, solve = false;

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--rings') rings = parseInt(args[++i]) || 8;
        else if (args[i] === '--sectors') sectors = parseInt(args[++i]) || 12;
        else if (args[i] === '--algo') algo = args[++i];
        else if (args[i] === '--seed') seed = parseInt(args[++i]);
        else if (args[i] === '--solve') solve = true;
    }

    console.log('\x1b[36m⭕ Circular Maze Generator (JavaScript)\x1b[0m');
    console.log(`📐 Параметры: ${rings} колец, ${sectors} секторов, алгоритм: ${algo}`);

    const gen = new CircularMaze(rings, sectors, algo, seed, solve);
    gen.generate();
    gen.printASCII();
    gen.saveJSON();
}

if (require.main === module) main();
