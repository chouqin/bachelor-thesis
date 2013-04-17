%%%%%%%%%%%%%%%%%%%%%%
% Call cvx to do optimize job
% A good example
% Pick A to be a full matrix or a diag matrix first
%%%%%%%%%%%%%%%%%%%%%%%


function A = cvx_optimize(data, S, D)

N = size(data, 1);
d = size(data, 2);

%%%%%%%%%%%%%%%%%%%%%%%%%%
% Diag Matrix A
%%%%%%%%%%%%%%%%%%%%%%%%%%
s_sum = zeros(1,d);
for i = 1:N
  for j = i+1:N
    d_ij = data(i,:) - data(j,:);
    s_sum = s_sum + S(i, j)^2 * d_ij.^2;
  end
end

cvx_flag = 'cvx begin'
cvx_begin
    variable x(d);
    d_sum = 0;
    for i = 1:N
        for j = i+1:N
            if D(i, j) ==1
                d_ij = data(i,:) - data(j,:);
                d_sum = sqrt((d_ij.^2)*x);
            end

        end
    end
    minimize(s_sum * x);
    subject to 
        d_sum * x >= 1;
        x >= 0;
cvx_end
A = diag(x); % for diag matrix


%%%%%%%%%%%%%%%%%%%%%%%%
% Full matrix A
%%%%%%%%%%%%%%%%%%%%%%%%
cvx_flag = 'cvx begin'
cvx_begin
    variable x(d, d);
    s_sum = 0;
    d_sum = 0;
    for i = 1:N
        for j = i+1:N
            d_ij = data(i,:) - data(j,:);
            distance = d_ij * x * d_ij';
            s_sum = s_sum + S(i, j) ^ 2 * distance;
            if D(i,j) == 1
                d_sum = d_sum + sqrt(distance);
            end
        end
    end 
    minimize(s_sum);
    subject to 
        d_sum >= 1;
        x >= 0;
        x == semidefinite(d);
cvx_end
A = x;  %for full matrix
