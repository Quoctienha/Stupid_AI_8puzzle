import pygame
import random
import heapq
from collections import deque

# Initialize Pygame
pygame.init()

#colors (r,g,b)
WHITE =(255,255,255)
BLACK =(0,0,0)
BLUE = (0,87,217)
DARKGREY =(40,40,40)
LIGHTGREY =(100,100,100)
BGCOLOUR = DARKGREY

#GAME SETTINGS
WIDTH = 1100
HEIGHT = 641
title = "8-puzzle game"
TILE_SIZE = 128
FONT = pygame.font.Font(None, 80)
    
   
# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(title)

#create a new puzzle
def create_puzzle():
    numbers = [1,2,3,4,5,6,7,8,0]
    random.shuffle(numbers)
    return numbers

#check if the game is solved
def is_solved(puzzle):
    return puzzle == [1, 2, 3, 4, 5, 6, 7, 8, 0]

#shuffle
def shuffle_puzzle(puzzle):
    new_puzzle = create_puzzle()
    for i in range(len(puzzle)):
        puzzle[i] = new_puzzle[i]

#draw buttons
def draw_button(ButtonText, posX, posY):
    # Button position
    button_rect = pygame.Rect(posX, posY, 150, 40)
    pygame.draw.rect(screen, WHITE, button_rect)
    
    # Add text
    button_font = pygame.font.Font(None, 40)
    button_text = button_font.render(ButtonText, True, BLACK)
    screen.blit(button_text, (posX + 10, posY + 10 ))
    return button_rect
    
#draw the game 
def draw_game(puzzle):
    screen.fill(BGCOLOUR)
       
    #draw when complete the puzzle
    if is_solved(puzzle):
        text = FONT.render("puzzle solved", True, WHITE)
        screen.blit(text, (50, 50+ TILE_SIZE*3))
        
    #draw the puzzle
    for row in range(3):
        for col in range(3):
            tile_value = puzzle[row * 3 + col]
            x = col * TILE_SIZE  +50
            y = row * TILE_SIZE  +50
            if tile_value != 0:
                pygame.draw.rect(screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE))
                #add number to he tile
                text = FONT.render(str(tile_value), True, BLACK)
                screen.blit(text, (x + TILE_SIZE//3 , y + TILE_SIZE//3))
            else:
                pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                
            #border
            pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE), 3)

# the events of pygame
def event(puzzle, shuffle_button, bfs_button, dfs_button, ucs_button, greedy_button, aStar_button):
    count_states = 0
    
    for event in pygame.event.get():
        #QUIT PLAYING
        if event.type == pygame.QUIT:
            pygame.quit() 
        # buttons event
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and shuffle_button.collidepoint(event.pos):
                shuffle_puzzle(puzzle) #shuffle the puzzle
            if event.button == 1 and bfs_button.collidepoint(event.pos):
                result = bfs(puzzle, count_states)  
                if result is not None:
                    solution, count_states = result  # Chỉ unpack nếu kết quả không phải là None
                    print("Solution found with BFS:", solution)
                    print("Steps:", len(solution))
                    print("States:", count_states)
                else:
                    print("No solution found with BFS.")
            if event.button == 1 and dfs_button.collidepoint(event.pos):
                result = dfs(puzzle, count_states)  
    
                if result is not None:
                    solution, count_states = result  # Chỉ unpack nếu kết quả không phải là None
                    print("Solution found with DFS:", solution)
                    print("Steps:", len(solution))
                    print("States:", count_states)
                else:
                    print("No solution found or exceeded depth limit with DFS.")
            if event.button == 1 and ucs_button.collidepoint(event.pos):
                result = ucs(puzzle, count_states)  
                if result is not None:
                    solution, count_states = result  # Chỉ unpack nếu kết quả không phải là None
                    print("Solution found with UCS:", solution)
                    print("Steps:", len(solution))
                    print("States:", count_states)
                else:
                    print("No solution found with UCS.")
            if event.button == 1 and greedy_button.collidepoint(event.pos):
                result = greedy_search(puzzle, count_states)  
                if result is not None:
                    solution, count_states = result  # Chỉ unpack nếu kết quả không phải là None
                    print("Solution found with GREEDY:", solution)
                    print("Steps:", len(solution))
                    print("States:", count_states)
                else:
                    print("No solution found with GREEDY.")
            if event.button == 1 and aStar_button.collidepoint(event.pos):
                result = a_star_search(puzzle, count_states)  
                if result is not None:
                    solution, count_states = result  # Chỉ unpack nếu kết quả không phải là None
                    print("Solution found with A*:", solution)
                    print("Steps:", len(solution))
                    print("States:", count_states)
                else:
                    print("No solution found with A*.")
                    
        #up, down, left, right 
        elif event.type == pygame.KEYDOWN:
            empty_index = puzzle.index(0)
    
            if event.key == pygame.K_UP and empty_index > 2:  # move the empty tile UP
                puzzle[empty_index], puzzle[empty_index - 3] = puzzle[empty_index - 3], puzzle[empty_index]
    
            elif event.key == pygame.K_DOWN and empty_index < 6:  # move the empty tile DOWN
                puzzle[empty_index], puzzle[empty_index + 3] = puzzle[empty_index + 3], puzzle[empty_index]
    
            elif event.key == pygame.K_LEFT and empty_index % 3 > 0:  # move the empty tile LEFT
                puzzle[empty_index], puzzle[empty_index - 1] = puzzle[empty_index - 1], puzzle[empty_index]
    
            elif event.key == pygame.K_RIGHT and empty_index % 3 < 2:  # move the empty tile RIGHT
                puzzle[empty_index], puzzle[empty_index + 1] = puzzle[empty_index + 1], puzzle[empty_index]
                    
# generate new states
def generate_states(puzzle):
    empty_index = puzzle.index(0)
    new_states = []

    if empty_index > 2:  # Move the empty tile UP
        new_state = puzzle[:]
        new_state[empty_index], new_state[empty_index - 3] = new_state[empty_index - 3], new_state[empty_index]
        new_states.append((new_state, "UP"))

    if empty_index < 6:  # Move the empty tile DOWN
        new_state = puzzle[:]
        new_state[empty_index], new_state[empty_index + 3] = new_state[empty_index + 3], new_state[empty_index]
        new_states.append((new_state, "DOWN"))

    if empty_index % 3 > 0:  # Move the empty tile LEFT
        new_state = puzzle[:]
        new_state[empty_index], new_state[empty_index - 1] = new_state[empty_index - 1], new_state[empty_index]
        new_states.append((new_state, "LEFT"))

    if empty_index % 3 < 2:  # Move the empty tile RIGHT
        new_state = puzzle[:]
        new_state[empty_index], new_state[empty_index + 1] = new_state[empty_index + 1], new_state[empty_index]
        new_states.append((new_state, "RIGHT"))

    return new_states
# %%
# Uninformed search
#BFS
def bfs(puzzle, count_states):
    queue = deque([(puzzle, [])])
    visited = set()  
    visited.add(tuple(puzzle)) 

    while queue:
        current_state, path = queue.popleft()

        if is_solved(current_state):
            return path, count_states  

        for neighbor, direction in generate_states(current_state):
            #count_states = count_states + len(generate_states(current_state))
            if tuple(neighbor) not in visited:
                visited.add(tuple(neighbor))
                queue.append((neighbor, path + [direction]))  # Cập nhật đường đi
                count_states +=1

    return None  

# DFS có giới hạn phạm vi
def dfs(puzzle, count_states, depth_limit = 100_000, current_depth=0):
    stack = [(puzzle, [])]  
    visited = set()  
    visited.add(tuple(puzzle)) 

    while stack:
        current_state, path = stack.pop()

        if is_solved(current_state):
            return path, count_states 

        if current_depth < depth_limit:  # Kiểm tra xem có vượt quá giới hạn độ sâu không
            for neighbor, direction in generate_states(current_state):
                if tuple(neighbor) not in visited:
                    visited.add(tuple(neighbor))
                    stack.append((neighbor, path + [direction]))  # Cập nhật đường đi
                    count_states += 1  
            current_depth += 1  

    return None  

def ucs(puzzle, count_states):
    # priority queue to store (cost, current_state, path)
    priority_queue = [(0, puzzle, [])]
    visited = set()  # to track visited nodes
    
    heapq.heapify(priority_queue)  # Initialize the priority queue (min-heap)
    visited.add(tuple(puzzle))

    while priority_queue:
        cost, current_state, path = heapq.heappop(priority_queue)  # Get the least-cost node

        if is_solved(current_state):
            return path, count_states  # Return the path and the total cost

        for neighbor, direction in generate_states(current_state):
            if tuple(neighbor) not in visited:
                visited.add(tuple(neighbor))
                heapq.heappush(priority_queue, (cost + 1, neighbor, path + [direction]))  # Add neighbor with updated cost
                count_states +=1
    return None # No solution found

# %%
#Imformed Search
def manhattan_distance(puzzle):
   distance = 0
   for i in range(9):
        if puzzle[i] != 0:
            distance += abs((i % 3) - ((puzzle[i] - 1) % 3)) + abs((i // 3) - ((puzzle[i] - 1) // 3))
   return distance

def greedy_search(puzzle, count_states):
    # Priority queue to store (h_cost, current_state, path)
    priority_queue = [(manhattan_distance(puzzle), puzzle, [])]
    visited = set()
    heapq.heapify(priority_queue)
    visited.add(tuple(puzzle))

    while priority_queue:
        h_cost, current_state, path = heapq.heappop(priority_queue)

        if is_solved(current_state):
            return path, count_states  # Return the path

        for neighbor, direction in generate_states(current_state):
            if tuple(neighbor) not in visited:
                visited.add(tuple(neighbor))
                heapq.heappush(priority_queue, (manhattan_distance(neighbor), neighbor, path + [direction]))
                count_states +=1
    return None  # No solution found

def a_star_search(puzzle, count_states):
    # Priority queue to store (f_cost, g_cost, current_state, path)
    priority_queue = [(manhattan_distance(puzzle), 0, puzzle, [])]
    visited = set()
    heapq.heapify(priority_queue)
    visited.add(tuple(puzzle))

    while priority_queue:
        f_cost, g_cost, current_state, path = heapq.heappop(priority_queue)

        if is_solved(current_state):
            return path, count_states  # Return the path

        for neighbor, direction in generate_states(current_state):
            if tuple(neighbor) not in visited:
                visited.add(tuple(neighbor))
                new_g_cost = g_cost + 1
                new_f_cost = new_g_cost + manhattan_distance(neighbor)
                heapq.heappush(priority_queue, (new_f_cost, new_g_cost, neighbor, path + [direction]))
                count_states +=1
    return None  # No solution found
# %%


# running the game
def running_game(puzzle):
    running = True
    while running: 
        draw_game(puzzle)
        #buttons
        shuffle_button = draw_button("Shuffle", WIDTH - 500 ,50 )
        bfs_button = draw_button("BFS", WIDTH - 500 , 100 )
        dfs_button = draw_button("DFS", WIDTH - 500 , 150 )
        ucs_button = draw_button("UCS", WIDTH - 500 , 200 )
        greedy_button = draw_button("Greedy", WIDTH - 500 , 250 )
        aStar_button = draw_button("A*", WIDTH - 500 , 300 )
        event(puzzle, shuffle_button, bfs_button, dfs_button, ucs_button, greedy_button, aStar_button)
        pygame.display.flip()

#the main function, where the code run
def main():
    puzzle1 =[6, 7, 4, 2, 3, 8, 0, 5,1]
    puzzle2 =[1, 2, 3, 4, 5, 6, 7, 0,8]
    puzzle = create_puzzle()
    running_game(puzzle)
    
    
if __name__ == "__main__":
    main()    
    
    