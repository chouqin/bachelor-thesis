%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% An implementation of the spectural clustering algorithm
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% get distance either directly or from features

% directly
% distance = load('data\flickr\distance.txt');

% from features
% remember to normalize features and do PCA analysis first
features = load('data\flickr\features.txt');
features = NormalizeFea(features,1);
[coe, score] = princomp(features);
features1 = score(:, 1:50);
distance = squareform(pdist(features1));

% get similarity from distance using Guassian Kernel
n=size(distance,1);
tmp=sum(sum(distance))/n/(n-1);
W = exp(-distance.^2/2/tmp/tmp);

% spectural clustering algorithm using similarity matrix
D = diag(sum(W));

L = D-W;
k = 6;

opt = struct('issym', true, 'isreal', true);

[V dummy] = eigs(L, D, k+1, 'SM', opt);

% spectural_idx = kmeans(V(:,1:k), k); % using kmeans to get index

[dummy spectural_idx]=max(V(:,1:k)');
