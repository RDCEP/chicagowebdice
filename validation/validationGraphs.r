  #Plot GAMS 2007 and webDICE Output

gamsDir <- "/Users/matthewgee/Dev/CI/chicagowebdice/GAMS/GAMSwebDICE"
webDirOpt <- "/Users/matthewgee/Dev/webDICE2/chicagowebdice/validation/verify2/verify.optimized"
webDirSim <- "/Users/matthewgee/Dev/webDICE2/chicagowebdice/validation/verify2/verify.unoptimized"
#webDir <- "/Users/matthewgee/Dev/webDICE2/chicagowebdice/validation/verify"
ORGgamsDir <- "/Users/matthewgee/Dev/webDICE2/chicagowebdice/validation"

setwd(gamsDir)
gamsData = read.csv(file = "sigma.csv", header = FALSE, sep = ",")
gamsData = data.frame(t(gamsData))
names(gamsData) = c("Y","CPC","IndEm","Miu")
CPCgams = as.numeric(levels(gamsData$Y))[gamsData$Y]
CPCgams = CPCgams[1:30]
MIUgams = as.numeric(levels(gamsData$Miu))[gamsData$Miu]
MIUgams = MIUgams[1:30]

#add = c(1:21)
#Y <- append(Y, add, after=39)

setwd(webDirOpt)
webDiceData = read.csv(file = "gams_None_None.csv", header = FALSE, sep=",")
#webDiceData = data.frame(t(webDiceData))
CPCwebDICE = webDiceData$V6[1:30]
#create year vector
decades = c(1:1:30)
plotData = data.frame(c(decades,CPCgams,CPCwebDICE))
plot <- ggplot(data = plotData, aes(x=decades, y = CPCgams)) + 
  geom_line(data = plotData, aes(y = CPCgams), color="red") +
  geom_line(data = plotData, aes(y = CPCwebDICE), color="blue")


plot = plot + 
  ggtitle("Optimized consumption per capita \n from DICE2007 GAMS code and webDICE\n with default paramters") +
  theme(plot.title = element_text(lineheight=.8, face="bold")) +
  xlab("# decades starting in 2005") +
  ylab("Consumption Per Capita")

plot

###Plot MIUs
setwd(webDir)
webDiceData = read.csv(file = "gams_None_None.csv", header = FALSE, sep=",")
#webDiceData = data.frame(t(webDiceData))
MIUwebDICE = webDiceData$V1[1:30]
#create year vector
decades = c(1:1:30)
plotData = data.frame(c(decades,MIUgams,MIUwebDICE))
plot <- ggplot(data = plotData, aes(x=decades, y = MIUgams)) + 
  geom_line(data = plotData, aes(y = MIUgams), color="red") +
  geom_line(data = plotData, aes(y = MIUwebDICE), color="blue")
plot = plot + 
  ggtitle("Optimized Miu \n from DICE2007 GAMS code and webDICE\n with default paramters") +
  theme(plot.title = element_text(lineheight=.8, face="bold")) +
  xlab("# decades starting in 2005") +
  ylab("Miu")

plot

## Unoptimized 
setwd(ORGgamsDir)
gamsData = read.csv(file = "dice_output.csv", header = FALSE, sep = ",")
gamsData = data.frame(t(gamsData))
names(gamsData) = c("Y","CPC","IndEm","Miu")
CPCgams = as.numeric(levels(gamsData$Y))[gamsData$Y]
CPCgams = CPCgams[1:30]
MIUgams = as.numeric(levels(gamsData$Miu))[gamsData$Miu]
MIUgams = MIUgams[1:30]

plotData = data.frame(c(decades,CPCgams,CPCwebDICE))
plot <- ggplot(data = plotData, aes(x=decades, y = CPCgams)) + 
  geom_line(data = plotData, aes(y = CPCgams), color="red") +
  geom_line(data = plotData, aes(y = CPCwebDICE), color="blue")


plot = plot + 
  ggtitle("Optimized consumption per capita \n from DICE2007 GAMS code and webDICE\n with default paramters") +
  theme(plot.title = element_text(lineheight=.8, face="bold")) +
  xlab("# decades starting in 2005") +
  ylab("Consumption Per Capita")

plot


#Combine data
#years <- c(1:60, 1:60)
#variables <- c(rep("webDice", 60), rep("GAMS", 60) )
#values <- c(webDiceData$V6, gamsData$Y)

#df <- data.frame(years, variables, values )

#d <- ggplot(df, aes(x=years, y=values, group=variables, colour=variables ) ) + 
 # geom_line(size=2)
#d