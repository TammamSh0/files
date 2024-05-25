from django.shortcuts import render
from django.http import HttpResponse
import numpy as np
import networkx as nx

def index(request):
    return render(request, 'optimization/index.html')

def solve(request):
    if request.method == 'POST':
        num_trucks = int(request.POST['num_trucks'])
        trucks = []
        paths = []
        
        for i in range(num_trucks):
            truck_capacity = int(request.POST[f'truck_capacity_{i}'])
            num_goods = int(request.POST[f'num_goods_{i}'])
            goods = []
            for j in range(num_goods):
                value = int(request.POST[f'good_value_{i}_{j}'])
                weight = int(request.POST[f'good_weight_{i}_{j}'])
                goods.append((value, weight))
            optimal_value, selected_goods = knapsack(truck_capacity, goods)
            trucks.append({'optimal_value': optimal_value, 'selected_goods': selected_goods})
        
            num_addresses = int(request.POST[f'num_addresses_{i}'])
            times = []
            for a in range(num_addresses):
                row = []
                for b in range(num_addresses):
                    if a != b:
                        time = int(request.POST[f'time_{i}_{a}_{b}'])
                        row.append(time)
                    else:
                        row.append(0)
                times.append(row)

            # حل مشكلة اختيار البضائع الأمثل
            optimal_value, selected_goods = knapsack(truck_capacity, goods)
        
            # حل مشكلة أقصر مسار
            shortest_path, shortest_distance = shortest_path_tsp(times)
            paths.append({'path': shortest_path, 'distance': shortest_distance})
        
        return render(request, 'optimization/results.html', 
                      {'trucks':trucks, 
                       'paths':paths})
    else:
        return HttpResponse("Invalid request method.", status=405)

# دالة حل مشكلة اختيار البضائع الأمثل باستخدام خوارزمية knapsack
def knapsack(capacity, items):
    n = len(items)
    dp = np.zeros((n + 1, capacity + 1))
    
    for i in range(1, n + 1):
        value, weight = items[i - 1]
        for w in range(capacity + 1):
            if weight <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight] + value)
            else:
                dp[i][w] = dp[i-1][w]
    
    optimal_value = int(dp[n][capacity])
    
    # استخراج البضائع المختارة
    selected_goods = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            value, weight = items[i - 1]
            selected_goods.append((value, weight))
            w -= weight
    
    return optimal_value, selected_goods

# دالة حل مشكلة أقصر مسار باستخدام خوارزمية TSP
def shortest_path_tsp(times):
    G = nx.Graph()
    n = len(times)
    
    for i in range(n):
        for j in range(i + 1, n):
            G.add_edge(i, j, weight=times[i][j])
    
    tsp_path = nx.approximation.traveling_salesman_problem(G, cycle=True)
    tsp_distance = sum(times[tsp_path[i]][tsp_path[i + 1]] for i in range(len(tsp_path) - 1))
    
    return tsp_path, tsp_distance
