%function [B, DCA, newData]=DCA(data,chunks,neglinks,useD)

%DCA function. 

%Input :

% data   - The data points as an d*n matrix, where n is the number of data points,

%          d the dimension of the data. Each data point is a row in the matrix.

%

% chunks - a vector of size n*1 describing the chunklets :

%          -1 in the i'th place says that point i doesn't belong to any

%          chunklet integer j in place i says that point i belongs to chunklet j.

%          The chunklets indexes should be 1:number_of chunklets

%

% neglinks - a matrix of size s*s describing the negative relationship

%            between s chunklets

%

% useD - optional. When not given, DCA is done in the original dimension

%        and B is full rank. When useD is given DCA is preceded by

%        constraints based LDA which reduces the dimension to useD. 

%        B in this case is of rank useD.

%

% Output:

% B       - the DCA suggested Mahalanobis matrix.

% DCA     - the DCA suggested transformation of the data

%           Its dimensions are (original data dimension)*(useD)

% newData - the data after the DCA transformation (A).

%  for every two original data points x1,x2 with new images (in newData) y1,y2:

%  (x2-x1)'*B*(x2-x1) = || (x2-x1)*A ||^2 = || y2-y1||^2 



function [B, DCA, newData]=DCA_func(data,chunks,neglinks,useD)



[d,n] = size(data);

if ~exist('useD','var')

    useD=d;

end



% subtract the mean

%TM=mean(data');

%data=data-TM'*ones(1,n);



%1. Compute means of chunks

s=max(chunks);

Cdata=[];

AllInds=[];

M=[];

for i=1:s

    inds=find(chunks==i);

    M(:,i)=mean(data(:,inds)');    

end



%2. Compute Cb

Cb=zeros(d,d);

N_d=0;

for j=1:s

    inds=find(neglinks(j,:)>0);

    for i=1:length(inds)

        Cb=Cb+((M(:,j)-M(:,inds(i)))*(M(:,j)-M(:,inds(i)))');

    end

    N_d=N_d+length(inds);

end

if (N_d==0),

    C_b=eye(d);

else

    Cb=Cb/N_d;

end



%3. Compute Cw

Cw=zeros(d,d);

N_w=0;

for j=1:s

    inds=find(chunks==j);

    for i=1:length(inds)

        Cw=Cw+(((data(:,inds(i))-M(:,j))*(data(:,inds(i))-M(:,j))'));

    end

    N_w=N_w+length(inds);

end

Cw=Cw/N_w;



%3. Diagonalize Cb

[eigVec, eigVal]=eig(Cb);

[index]=find(abs(diag(eigVal))>1e-9);  % find Non-Zero EigVals 

R=[];

%if exist('useD','var')

if (useD<d)

    [YeigVal,index]=sort(-abs(diag(eigVal))); %decreasing order

    R=[eigVec(:,index(1:useD))];

else

    R=[eigVec(:,index)];	% Each col of D is an eigenvector

end



Db=R'*Cb*R;

Z=R*(Db)^(-0.5);

% Diagonalize Z'*Cw*Z

Cz=Z'*Cw*Z;

[eigVec, eigVal] = eig(Cz);

Dw=eigVal;

DCA=(Dw^(-0.5))*eigVec'*Z';

B=DCA'*DCA;

newData=DCA*data;

%newData=DCA*(data+TM'*ones(1,n));

