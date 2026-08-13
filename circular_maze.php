<?php
// circular_maze.php — PHP версия

class CircularMaze {
    private $rings, $sectors, $algo, $seed, $solve;
    private $maze, $path;

    public function __construct($rings, $sectors, $algo = 'dfs', $seed = null, $solve = false) {
        $this->rings = $rings;
        $this->sectors = $sectors;
        $this->algo = $algo;
        $this->seed = $seed;
        $this->solve = $solve;
        $this->maze = null;
        $this->path = null;
        if ($seed !== null) mt_srand($seed);
    }

    private function getNeighbors($ring, $sector) {
        $neighbors = [];
        if ($ring > 0) $neighbors[] = [$ring-1, $sector, 0];
        if ($ring < $this->rings-1) $neighbors[] = [$ring+1, $sector, 1];
        $neighbors[] = [$ring, ($sector-1+$this->sectors)%$this->sectors, 2];
        $neighbors[] = [$ring, ($sector+1)%$this->sectors, 3];
        return $neighbors;
    }

    private function generateDFS() {
        $maze = array_fill(0, $this->rings, array_fill(0, $this->sectors, ['v' => true, 'h' => true]));
        $stack = [[0, 0]];
        $visited = ['0,0' => true];

        while (!empty($stack)) {
            $pos = end($stack);
            $ring = $pos[0];
            $sector = $pos[1];
            $neighbors = $this->getNeighbors($ring, $sector);
            shuffle($neighbors);

            $found = false;
            foreach ($neighbors as $n) {
                list($nr, $ns, $dir) = $n;
                $key = "$nr,$ns";
                if (isset($visited[$key])) continue;
                $visited[$key] = true;
                if ($dir == 0) $maze[$nr][$ns]['h'] = false;
                else if ($dir == 1) $maze[$ring][$sector]['h'] = false;
                else if ($dir == 2) $maze[$ring][($sector-1+$this->sectors)%$this->sectors]['v'] = false;
                else $maze[$ring][$sector]['v'] = false;
                $stack[] = [$nr, $ns];
                $found = true;
                break;
            }
            if (!$found) array_pop($stack);
        }
        return $maze;
    }

    public function generate() {
        $this->maze = $this->generateDFS();
        if ($this->solve) $this->path = $this->solveMaze();
        return $this->maze;
    }

    private function solveMaze() {
        $stack = [[[0, 0]]];
        $visited = ['0,0' => true];

        while (!empty($stack)) {
            $path = array_pop($stack);
            $last = end($path);
            list($ring, $sector) = $last;
            if ($ring == $this->rings-1) return $path;

            foreach ($this->getNeighbors($ring, $sector) as $n) {
                list($nr, $ns, $dir) = $n;
                $key = "$nr,$ns";
                if (isset($visited[$key])) continue;
                $hasWall = false;
                if ($dir == 0) $hasWall = $this->maze[$nr][$ns]['h'];
                else if ($dir == 1) $hasWall = $this->maze[$ring][$sector]['h'];
                else if ($dir == 2) $hasWall = $this->maze[$ring][($sector-1+$this->sectors)%$this->sectors]['v'];
                else $hasWall = $this->maze[$ring][$sector]['v'];
                if (!$hasWall) {
                    $visited[$key] = true;
                    $newPath = $path;
                    $newPath[] = [$nr, $ns];
                    $stack[] = $newPath;
                }
            }
        }
        return null;
    }

    public function printASCII() {
        echo "\033[36m\nКарта лабиринта (вид сверху):\033[0m\n";
        echo "\033[33m  Колец: {$this->rings}, Секторов: {$this->sectors}\033[0m\n";
        for ($ring = 0; $ring < $this->rings; $ring++) {
            echo "R$ring: ";
            for ($sector = 0; $sector < $this->sectors; $sector++) {
                $v = $this->maze[$ring][$sector]['v'] ? '|' : ' ';
                $h = $this->maze[$ring][$sector]['h'] ? '─' : ' ';
                echo $v . $h;
            }
            echo "\n";
        }
    }
}

function main($argv) {
    $rings = 8;
    $sectors = 12;
    $algo = 'dfs';
    $seed = null;
    $solve = false;

    for ($i = 1; $i < count($argv); $i++) {
        if ($argv[$i] == '--rings') { $rings = (int)$argv[++$i]; }
        else if ($argv[$i] == '--sectors') { $sectors = (int)$argv[++$i]; }
        else if ($argv[$i] == '--algo') { $algo = $argv[++$i]; }
        else if ($argv[$i] == '--seed') { $seed = (int)$argv[++$i]; }
        else if ($argv[$i] == '--solve') { $solve = true; }
    }

    echo "\033[36m⭕ Circular Maze Generator (PHP)\033[0m\n";
    echo "📐 Параметры: {$rings} колец, {$sectors} секторов, алгоритм: {$algo}\n";

    $gen = new CircularMaze($rings, $sectors, $algo, $seed, $solve);
    $gen->generate();
    $gen->printASCII();
}

$argc = $_SERVER['argc'] ?? 0;
$argv = $_SERVER['argv'] ?? [];
main($argv);
?>
