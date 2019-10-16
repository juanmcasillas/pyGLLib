# pyGLLib
A simple but modern python GL library focused on rapid prototyping

# R script

```
data <- read.csv("/Archive/Src/pyGLLib/data.txt",sep=";")
x <- data$X.x
y <- data$y
z <- data$e
options(repos='http://cran.rstudio.com/')
install.packages("plotly")
p <- plot_ly(data, x = x, y = y, z = z)
p
```
