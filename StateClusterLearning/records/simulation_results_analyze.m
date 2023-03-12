clear;
clc;
% 
load q_learning_s2.mat
figure(1);
plot(rewards,'.-');
watchPoints=[100,round(length(rewards)*0.4)  round(length(rewards)*0.9)];
figure(2);
for i=1:3
   subplot(1,3,i);
   wf=waterfall(i,:,:);
   wf=reshape(wf,100,10);
   imagesc(wf);title(['iter=' num2str(watchPoints(i))]);
end


    

