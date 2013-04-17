%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Plot final result
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

dresult = load('data\blogcatalog\result\node_max\summary.txt');

point_num = size(dresult, 1);

x = dresult(:, 1)';
dpurity = dresult(:, 2)';
kpurity = 0.395662368113 * ones(point_num, 1);  % blogcatalog k purity
% kpurity = 0.414419695193 * ones(point_num, 1); %blogcatalog-b k purity

plot(x,dpurity,'--rs',x,kpurity,'-')

xlabel('Local information region size');       %  add axis labels and plot titl
ylabel('Purity');
title('Purity of kmeans and DSHRINK Clustering');
legend('DSHRINK','kmeans');
