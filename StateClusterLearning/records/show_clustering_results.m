clear;
clc;
load cluster_results_s2_n10.mat
N=size(label,1);
M=size(label,2);
for m=1:M
    class(m).elements=[]
end

for n=1:N
    m=label2index(label(n,:));
    class(m).elements=[class(m).elements n];
    index(n)=m;
end

figure(1)
[x y]=hist(index);
bar(y,x/N);



for n=1:9
    figure(2);subplot(3,3,n);
    m=class(2).elements(n+10);
    s=reshape(states(m,:,:),100,10);
    imagesc(s);
end

function index=label2index(label)
N=length(label);
for n=1:N
    if(label(n)==1)
        index=n
        return
    end
    
end
index=-1
end