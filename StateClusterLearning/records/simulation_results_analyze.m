clear;
clc;
% 
load dqn_learning_s2.mat
figure(1);
plot(rewards,'.-');
hold on;
stem(watchPoints/10,rewards(watchPoints/10),'o'); hold off;

figure(2);
N=length(watchPoints);
for i=1:N
   subplot(1,N,i);
   wf=waterfall(i,:,:);
   wf=reshape(wf,100,10);
   imagesc(wf);title(['iter=' num2str(watchPoints(i)/10)]);
end



    

