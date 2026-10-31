import sys
import heapq
import signal


stop = False


def on_sigterm(signum, frame):
    global stop
    stop = True

def read_graph():
    lines = sys.stdin.buffer.read().split(b'\n')
    n, m, _ = map(int, lines[0].split())
    graph = [[] for _ in range(n)]
    reverse_graph = [[] for _ in range(n)]
    
    for u in range(n):
        for x in map(int, lines[u + 1].split()):
            v = x - 1
            graph[u].append(v)
            reverse_graph[v].append(u)
            
    return n, graph, reverse_graph

def find_strong_components(graph, reverse_graph):
    n = len(graph)
    used = bytearray(n)
    order = []
    
    for start in range(n):
        if used[start]:
            continue
        
        used[start] = 1
        stack = [(start, 0)]
        
        while stack:
            v, i = stack[-1]
            
            if i < len(graph[v]):
                w = graph[v][i]
                stack[-1] = (v, i + 1)
                
                if not used[w]:
                    used[w] = 1
                    stack.append((w, 0))
            else:
                order.append(v)
                stack.pop()
                    
    c = [-1] * n
    components = []
    
    for start in reversed(order):
        if c[start] != -1:
            continue
        
        cid = len(components)
        nodes = []
        stack = [start]
        c[start] = cid
        
        while stack:
            v = stack.pop()
            nodes.append(v)
            
            for w in reverse_graph[v]:
                if c[w] == -1:
                    c[w] = cid
                    stack.append(w)
        components.append(nodes)
    
    return components

def process_component(nodes, graph, reverse_graph, ans, active, indeg, outdeg, in_queue, version):
    n = len(nodes)
    
    if len(nodes) == 1:
        u = nodes[0]
        
        if u in graph[u]:
            ans.add(u)
        return
    
    for u in nodes:
        active[u] = 1
    
    for u in nodes:
        for v in graph[u]:
            if active[v]:
                outdeg[u] += 1
                indeg[v] += 1
    queue = []
    
    def enqueue(u):
        if active[u] and (indeg[u] == 0 or outdeg[u] == 0):
            if not in_queue[u]:
                in_queue[u] = 1
                queue.append(u)
    
    heap = []
    
    def push(v):
        if not active[v]:
            return
        
        if indeg[v] == 0 or outdeg[v] == 0:
            return
        
        score = indeg[v] * outdeg[v] / (indeg[v] + outdeg[v])
        version[v] += 1
        heapq.heappush(heap, (-score, version[v], v))
        
    for v in nodes:
        enqueue(v)
        push(v)
    
    def remove_v(v, flag):
        if not active[v]:
            return
        
        active[v] = 0
        
        if flag:
            ans.add(v)
        
        for u in graph[v]:
            if active[u]:
                indeg[u] -= 1
                enqueue(u)
                push(u)
        
        for fr in reverse_graph[v]:
            if active[fr]:
                outdeg[fr] -= 1
                enqueue(fr)
                push(fr)
    while True:
        while queue:
            v = queue.pop()
            in_queue[v] = 0
            
            if active[v] and (indeg[v] == 0 or outdeg[v] == 0):
                remove_v(v, False)
        
        chosen = -1
        
        while heap:
            neg_score, ver, v = heapq.heappop(heap)
            
            if not active[v] or ver != version[v]:
                continue
            
            if indeg[v] == 0 or outdeg[v] == 0:
                continue
            
            chosen = v
            break
        
        if chosen == - 1:
            break
        
        remove_v(chosen, True)
    
    for v in nodes:
        active[v] = 0
        indeg[v] = 0
        outdeg[v] = 0
        in_queue[v] = 0
        version[v] = 0
        
def is_acyclic(graph, ans):
    n = len(graph)
    removed = bytearray(n)
    
    for v in ans:
        if not 0 <= v < n or removed[v]:
            return False
        removed[v] = 1
    
    indeg = [0] * n
    remain = n - len(ans)
    
    for u in range(n):
        if removed[u]:
            continue
        
        for v in graph[u]:
            if not removed[v]:
                indeg[v] += 1
                
    queue = [v for v in range(n) if not removed[v] and indeg[v] == 0]
    checked = 0
    head = 0
    
    while head < len(queue):
        u = queue[head]
        head += 1
        checked += 1
        
        for v in graph[u]:
            if not removed[v]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    queue.append(v)
                    
    return checked == remain

def main():
    signal.signal(signal.SIGTERM, on_sigterm)
    
    n, graph, reversed_graph = read_graph()
    best = list(range(1, n + 1))
    
    components = find_strong_components(graph, reversed_graph)
    
    if components is None or stop:
        sys.stdout.write(''.join(f'{v}\n' for v in best))
        sys.stdout.flush()
        return
    
    ans = set()
    active = bytearray(n)
    indeg = [0] * n
    outdeg = [0] * n
    in_queue = bytearray(n)
    version = [0] * n

    for nodes in components:
        if stop:
            break
        
        if len(nodes) > 1:
            end = process_component(nodes, graph, reversed_graph, ans, active, indeg, outdeg, in_queue, version)
            
            if not end:
                break
        else:
            v = nodes[0]
            
            if v in graph[v]:
                ans.add(v)
                
    if not stop and is_acyclic(graph, ans):
        best = sorted(v + 1 for v in ans)
        
    sys.stdout.write("".join(str(v) + "\n" for v in best))
    sys.stdout.flush()
    
    
if __name__ == "__main__":
    main()
    