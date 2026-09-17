% regen_c3.m — 循环3 图形重生成（z1 底影互换 / z2 收紧空轴 / 术语统一 / 图内字号提档）
% 数据源：FM\_ppt_run\assets\simdata_r15.mat（2026-09-15 round16 仿真，只读，不重跑仿真）
% 输出：examples\fm_iq_receiver_rmo01a\assets\ 下 4 张 PNG（覆盖前已备份 *.bak-c3）
% 口径与 regen_spec_r14.m 完全一致：窗 20–80ms、600 点、df=fs/600 谱线落 k*50Hz bin、全谱归一化
clear; close all;
ad = 'D:\wanglei\project\TDA7707_GNSS\E_project\multi_agent_PPT_zcode\examples\fm_iq_receiver_rmo01a\assets';
S  = load('D:\wanglei\project\TDA7707_GNSS\E_project\FM\_ppt_run\assets\simdata_r15.mat');
fs = 1e4;
TEAL=[0.098 0.439 0.518]; BLUE=[0.180 0.459 0.714]; RED=[0.753 0 0];
GRY=[0.35 0.35 0.35];
newf = @(sz) figure('Visible','off','Color','w','Units','pixels','Position',[60 60 sz(1) sz(2)]);
expf = @(h,nm) exportgraphics(h, fullfile(ad,nm), 'Resolution', 200);
axf  = @(h) set(findall(h,'-property','FontName'),'FontName','Microsoft YaHei');
fsz  = @(h,v) set(findall(h,'-property','FontSize'),'FontSize',v);   % 全局字号（轴刻度/标签/图例统一档）

% ---------- 窗口（与 r14 口径一致） ----------
grid_ = (0.02:1/fs:0.08)';
rs  = @(t,v) interp1(t,v,grid_,'linear');
z1w = rs(S.t1,  S.z1);   z2w = rs(S.t2, S.z2);
bbw = rs(S.tbb, S.bb);   b0w = rs(S.t0, S.bb0);
z1w = z1w(1:600); z2w = z2w(1:600); bbw = bbw(1:600); b0w = b0w(1:600);
N = 600; df = fs/N;

    function [fA, dBA] = stems_c(x, dfq, fLo, fHi)
        X = fft(x); Nf = numel(x);
        f = (0:Nf-1)'*dfq;
        f(f>=Nf*dfq/2) = f(f>=Nf*dfq/2) - Nf*dfq;
        A = abs(X);
        dB = 20*log10(A+eps); dB = dB - max(dB);
        sel = f>=fLo & f<=fHi;
        fA = f(sel)*1e-3; dBA = dB(sel);
    end
    function draw_stems(ax, fA, dBA, col, lw)
        for k=1:numel(fA)
            plot(ax,[fA(k) fA(k)],[-100 dBA(k)],'-','Color',col,'LineWidth',lw);
            plot(ax,fA(k),dBA(k),'v','MarkerSize',5,'MarkerFaceColor',col,'MarkerEdgeColor',col);
        end
    end

%% ===== B. z1 复频谱（P8 左）——底影颜色与簇色对齐：有用(+)=浅红、镜像(−)=浅蓝 =====
[fP,dP] = stems_c(z1w, df, 100, 700);
[fM,dM] = stems_c(z1w, df, -700, -100);
h=newf([980 560]); ax=axes(h); hold(ax,'on');
patch(ax,[0.15 0.65 0.65 0.15],[-70 -70 5 5],[0.97 0.93 0.92],'EdgeColor','none'); uistack(ax,'bottom');
patch(ax,[-0.65 -0.15 -0.15 -0.65],[-70 -70 5 5],[0.90 0.96 0.97],'EdgeColor','none'); uistack(ax,'bottom');
draw_stems(ax, fP, dP, RED, 2.0);
draw_stems(ax, fM, dM, BLUE, 2.0);
grid(ax,'on'); xlim(ax,[-1.5 1.5]); ylim(ax,[-70 5]);
xlabel(ax,'f (kHz)'); ylabel(ax,'|Z_1(f)| (dB, 归一化)');
text(ax,0.40,3,'有用 → +400 Hz','Color',RED,'FontWeight','bold','FontSize',13,'HorizontalAlignment','center');
text(ax,-0.40,3,'镜像 → -400 Hz','Color',BLUE,'FontWeight','bold','FontSize',13,'HorizontalAlignment','center');
text(ax,0.72,-24,{'阴影 = 边带范围 ±4×50 Hz','复数混频不折叠 → 两簇彻底分开'},'FontSize',12,'Color',GRY,'BackgroundColor',[1 1 1],'Margin',1);
axf(h); fsz(h,12); expf(h,'F_z1_spectrum_r14.png'); close(h);

%% ===== D. z2 复频谱（P10）——收紧右缘空轴 + 字号提档 =====
[fP,dP] = stems_c(z2w, df, -300, 300);
[fM,dM] = stems_c(z2w, df, -1100, -500);
h=newf([980 560]); ax=axes(h); hold(ax,'on');
draw_stems(ax, fP, dP, RED, 2.0);
draw_stems(ax, fM, dM, BLUE, 2.0);
grid(ax,'on'); xlim(ax,[-1.5 0.6]); ylim(ax,[-70 5]);
xlabel(ax,'f (kHz)'); ylabel(ax,'|Z_2(f)| (dB, 归一化)');
text(ax,0.0,3,'有用 → 0 (零中频)','Color',RED,'FontWeight','bold','FontSize',13,'HorizontalAlignment','center');
text(ax,-0.80,3,'镜像 → -800 Hz','Color',BLUE,'FontWeight','bold','FontSize',13,'HorizontalAlignment','center');
plot(ax,[-1.3 -0.55],[-12.04 -12.04],':','Color',BLUE,'LineWidth',1.2);
text(ax,-1.28,-15,'理论 -20lg\gamma = -12.04 dB','Color',BLUE,'FontSize',12,'BackgroundColor',[1 1 1],'Margin',1);
axf(h); fsz(h,12); expf(h,'F_z2_spectrum_r14.png'); close(h);

%% ===== E. 基带 LPF 后镜像开（P12 左）=====
[fP,dP] = stems_c(bbw, df, -300, 300);
[fM,dM] = stems_c(bbw, df, -1100, -500);
h=newf([980 560]); ax=axes(h); hold(ax,'on');
draw_stems(ax, fP, dP, RED, 2.0);
draw_stems(ax, fM, dM, BLUE, 1.4);
grid(ax,'on'); xlim(ax,[-1.5 0.5]); ylim(ax,[-70 5]);
xlabel(ax,'f (kHz)'); ylabel(ax,'|Z_{BB}(f)| (dB, 归一化)');
text(ax,0.0,3,'有用：DC ± 4×50 Hz 边带','Color',RED,'FontWeight','bold','FontSize',13,'HorizontalAlignment','center');
text(ax,-0.80,3,'镜像残余','Color',BLUE,'FontWeight','bold','FontSize',13,'HorizontalAlignment','center');
plot(ax,[-1.3 -0.55],[-44.8 -44.8],':','Color',BLUE,'LineWidth',1.2);
text(ax,-1.28,-48.5,'镜像残余 -44.8 dBc（LPF 净压 32.9 dB）','Color',BLUE,'FontWeight','bold','FontSize',12,'BackgroundColor',[1 1 1],'Margin',1);
axf(h); fsz(h,12); expf(h,'F_bb_on_r14.png'); close(h);

%% ===== F. 基带 LPF 后镜像关（P12 右）=====
[fP,dP] = stems_c(b0w, df, -300, 300);
[fM,dM] = stems_c(b0w, df, -1100, -500);
h=newf([980 560]); ax=axes(h); hold(ax,'on');
draw_stems(ax, fP, dP, RED, 2.0);
draw_stems(ax, fM, dM, TEAL, 1.2);
grid(ax,'on'); xlim(ax,[-1.5 0.5]); ylim(ax,[-70 5]);
xlabel(ax,'f (kHz)'); ylabel(ax,'|Z_{BB}(f)| (dB, 归一化)');
text(ax,0.0,3,'有用：DC ± 4×50 Hz 边带','Color',RED,'FontWeight','bold','FontSize',13,'HorizontalAlignment','center');
text(ax,-0.80,3,'无镜像谱线','Color',TEAL,'FontWeight','bold','FontSize',13,'HorizontalAlignment','center');
plot(ax,[-1.3 -0.55],[-54.7 -54.7],':','Color',TEAL,'LineWidth',1.2);
text(ax,-1.28,-48.5,'底噪 -54.7 dBc（无镜像谱线）','Color',TEAL,'FontWeight','bold','FontSize',12,'BackgroundColor',[1 1 1],'Margin',1);
axf(h); fsz(h,12); expf(h,'F_bb_off_r14.png'); close(h);

%% ===== G. IQ 轨迹（P14 左）——术语统一"四极点级联" + 字号提档 =====
env = abs(bbw);                 % 20–80ms 窗内基带包络（6000 点）
rip = (max(env)-min(env))/2/mean(env);
fprintf('envelope ripple = %.1f%% (deck 口径 27.4%%)\n', rip*100);
dec = 6;
h=newf([700 640]); ax=axes(h); hold(ax,'on');
plot(ax, real(bbw(1:dec:end)), imag(bbw(1:dec:end)), '.', 'Color',TEAL,'MarkerSize',7);
th=linspace(0,2*pi,256); mrE = mean(env);
plot(ax, mrE*cos(th), mrE*sin(th),'--','Color',[0.6 0.6 0.6],'LineWidth',1);
axis(ax,'equal'); grid(ax,'on');
xlabel(ax,'I (V)'); ylabel(ax,'Q (V)');
legend(ax,{'(I,Q) 轨迹样本','平均半径圆'},'Location','southeast','FontSize',12);
text(ax, min(xlim)+0.03*diff(xlim), max(ylim)-0.05*diff(ylim), ...
    {'纹波来源：IF LPF(四极点级联) 带内倾斜','|H(600)|≈0.88 vs |H(200)|≈1.0'},'FontSize',12,'Color',GRY);
title(ax,sprintf('基带矢量轨迹：近圆，包络纹波 ±%.1f%%',rip*100),'FontWeight','bold','FontSize',13);
axf(h); fsz(h,12); expf(h,'F_iq_circle.png'); close(h);

disp('C3 FIGS DONE');
