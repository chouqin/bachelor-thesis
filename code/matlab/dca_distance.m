%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Call DCA to learn the distance metric
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


data = load('data\blogcatalog-b\pca_features.txt');
chunks = load('data\blogcatalog-b\chunks.txt');
neglinks = load('data\blogcatalog-b\neglinks.txt');

[A, DCA1, newData]=DCA(data',chunks, neglinks);

N = size(data, 1); % num of nodes
distance = zeros(N);
for i = 1:size(data, 1)
    for j = i+1:size(data, 1)
        d_ij = data(i, :) - data(j, :);
        distance(i, j) = sqrt(d_ij * A * d_ij');
        distance(j, i) = distance(i, j);
    end
end

dlmwrite('data\blogcatalog-b\dca_distance.txt', distance);
