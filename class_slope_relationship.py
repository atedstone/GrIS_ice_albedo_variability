# 20th

slopes_msk = slopes.slope.salem.roi(shape=shpf)
class_msk = uav.classified.salem.roi(shape=shpf)

combo = pd.DataFrame({
	'slope':slopes_msk.sel(time='2017-07-20').to_pandas().stack(),
	'class':class_msk.sel(time='2017-07-20').to_pandas().stack() 
	})

combo = combo.dropna()

figure(),sns.boxplot(x='class',y='slope',data=combo)    