# circular_maze.rb — Ruby версия

class CircularMaze
  attr_reader :maze, :path

  def initialize(rings, sectors, algo = 'dfs', seed = nil, solve = false)
    @rings = rings
    @sectors = sectors
    @algo = algo
    @seed = seed
    @solve = solve
    @maze = nil
    @path = nil
    @rng = seed ? Random.new(seed) : Random.new
  end

  def get_neighbors(ring, sector)
    neighbors = []
    neighbors << [ring-1, sector, 0] if ring > 0
    neighbors << [ring+1, sector, 1] if ring < @rings - 1
    neighbors << [ring, (sector-1+@sectors)%@sectors, 2]
    neighbors << [ring, (sector+1)%@sectors, 3]
    neighbors
  end

  def generate_dfs
    maze = Array.new(@rings) { Array.new(@sectors) { {v: true, h: true} } }
    stack = [[0, 0]]
    visited = Set.new
    visited.add([0, 0])

    while !stack.empty?
      ring, sector = stack.last
      neighbors = get_neighbors(ring, sector).shuffle(random: @rng)

      found = false
      neighbors.each do |nr, ns, dir|
        next if visited.include?([nr, ns])
        visited.add([nr, ns])
        case dir
        when 0 then maze[nr][ns][:h] = false
        when 1 then maze[ring][sector][:h] = false
        when 2 then maze[ring][(sector-1+@sectors)%@sectors][:v] = false
        when 3 then maze[ring][sector][:v] = false
        end
        stack << [nr, ns]
        found = true
        break
      end
      stack.pop unless found
    end
    maze
  end

  def generate
    @maze = generate_dfs
    @path = solve_maze if @solve
    @maze
  end

  def solve_maze
    stack = [[[0, 0]]]
    visited = Set.new
    visited.add([0, 0])

    while !stack.empty?
      path = stack.pop
      ring, sector = path.last
      return path if ring == @rings - 1

      get_neighbors(ring, sector).each do |nr, ns, dir|
        next if visited.include?([nr, ns])
        has_wall = case dir
        when 0 then @maze[nr][ns][:h]
        when 1 then @maze[ring][sector][:h]
        when 2 then @maze[ring][(sector-1+@sectors)%@sectors][:v]
        when 3 then @maze[ring][sector][:v]
        end
        unless has_wall
          visited.add([nr, ns])
          new_path = path.dup << [nr, ns]
          stack << new_path
        end
      end
    end
    nil
  end

  def print_ascii
    puts "\e[36m\nКарта лабиринта (вид сверху):\e[0m"
    puts "\e[33m  Колец: #{@rings}, Секторов: #{@sectors}\e[0m"
    @rings.times do |ring|
      print "R#{ring}: "
      @sectors.times do |sector|
        v = @maze[ring][sector][:v] ? '|' : ' '
        h = @maze[ring][sector][:h] ? '─' : ' '
        print v + h
      end
      puts
    end
  end
end

def main
  rings = 8
  sectors = 12
  algo = 'dfs'
  seed = nil
  solve = false

  args = ARGV
  i = 0
  while i < args.size
    case args[i]
    when '--rings' then rings = args[i+1].to_i; i += 2
    when '--sectors' then sectors = args[i+1].to_i; i += 2
    when '--algo' then algo = args[i+1]; i += 2
    when '--seed' then seed = args[i+1].to_i; i += 2
    when '--solve' then solve = true; i += 1
    else i += 1
    end
  end

  puts "\e[36m⭕ Circular Maze Generator (Ruby)\e[0m"
  puts "📐 Параметры: #{rings} колец, #{sectors} секторов, алгоритм: #{algo}"

  gen = CircularMaze.new(rings, sectors, algo, seed, solve)
  gen.generate
  gen.print_ascii
end

main if __FILE__ == $0
