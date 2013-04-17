function similarity = compute_similarity(i, j, edges)
num1 = 0;
num2 = 0;
num_total = 0;
for k = 1:9
    edge_i = has_edge(i, k, edges);
    edge_j = has_edge(j, k, edges);
    if edge_i
        num1 = num1 + 1;
    end
    if edge_j
        num2 = num2 + 1;
    end
    if edge_i && edge_j
        num_total = num_total + 1;
    end
end
similarity = num_total / sqrt(num1 * num2);
% similarity = 1;
    

function func = has_edge(i, j, edges)
func = 0;
for k = 1:size(edges, 1)
    if isequal(edges(k, :), [i j]) || isequal(edges(k, :), [j i])
        func = 1;
        break;
    end
end
