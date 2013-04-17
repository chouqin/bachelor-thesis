%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% sample a set of nodes from the blogcatalog dataset
% - First select 6 category
% - Then pick the nodes that belongs to any one of these category 
% - set the features, edges, and categories for these nodes
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

load('data\blogcatalog\blogcatalog6k.mat');

nodes_sample = [];
num_nodes_total = size(usertag, 1);

%selected category: 2, 10, 11, 32, 5, 12
selected_category = [2, 10, 11, 32, 5, 12];
selected_category_num = size(selected_category, 2);


% pick nodes
for i=1:num_nodes_total
    has_category = 0;
    for j =1:selected_category_num
        if usercategory(i, selected_category(j)) == 1
            has_category = 1;
            break;
        end
    end
   
    if has_category && sum(usertag(i, :)) != 0
        nodes_sample = [nodes_sample; i];
    end
end

nodes_num = size(nodes_sample, 1);
feature_num = size(usertag, 2);

% set features
features = zeros(nodes_num, feature_num);
for i = 1:nodes_num
    features(i, :) = usertag(nodes_sample(i), :);
end

% set edges
edges = [];
for i = 1:nodes_num
    for j = i+1:nodes_num
        if friendship(nodes_sample(i), nodes_sample(j)) == 1
            edges = [edges; [i, j]; [j i]];
        end
    end
end

% set categories
usercategory_use = zeros(nodes_num, selected_category_num);

for i = 1:nodes_num
    for j = 1:selected_category_num
        usercategory_use(i, j) = usercategory(nodes_sample(i), selected_category(j));
    end
end

% output 
dlmwrite('data\blogcatalog\features.txt', features);
dlmwrite('data\blogcatalog\edges.txt', edges);
dlmwrite('data\blogcatalog\usercategory.txt', usercategory_use);
