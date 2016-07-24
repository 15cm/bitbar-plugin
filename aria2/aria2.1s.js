#!/usr/bin/env /path/to/the/node/executable
const bitbar = require('bitbar')
const Aria2 = require('aria2')
const path = require('path')
const sprintf = require('sprintf-js').sprintf

// Change to your own config
var aria2 = new Aria2(
  {
    host: 'localhost',
    port: 6800,
    secure: false,
    secret: 'your token',
    path: '/jsonrpc',
    jsonp: false
  }
)

var bytesToReadable = (bytes, precision = 1) => {
  var dWidth = 4
  if(bytes > 1000000000){
    return sprintf(`%${dWidth + precision}.${precision}f`, bytes / 1000000000) + 'GB'
  } else if (bytes > 1000000){
    return sprintf(`%${dWidth + precision}.${precision}f`, bytes / 1000000) + 'MB'
  } else {
    return sprintf(`%${dWidth + precision}.${precision}f`, bytes / 1000) + 'KB'
  }
}

var genTaskStatus = task => {
  if(task.files.length > 0 && task.files[0].length > 0)
    return {
      type: task.status,
      name: path.basename(task.files[0].path),
      size: task.totalLength,
      percentage: task.completedLength / task.totalLength,
      downloadSpeed: task.downloadSpeed
    }
  else return null
}

var taskStatusToString = status => {
  var nameWidth = 40
  var progressWidth = 20
  var barLength = Number.parseInt(status.percentage * progressWidth)

  var nameStr = sprintf(`%-${nameWidth}.${nameWidth}s`, status.name)
  // Padding task name with '...' if it is too long
  if(status.name.length > nameWidth){
     nameStr = nameStr.substring(0,nameStr.length - 3) + '...'
  }

  var typeStr = ''
  switch(status.type) {
      case 'active':
        typeStr = '📶'
        break
      case 'waiting':
        typeStr = '🕒'
        break
      case 'paused':
        typeStr = '⏸'
        break
      case 'complete':
        typeStr = '✅'
        break
      default:
        typeStr = '❎'
  }
  var sizeStr = bytesToReadable(status.size)
  var percentageStr = sprintf(`[%-${progressWidth}s]%-6.6s`,
                              (new Array(barLength)).fill('=').join(''),
                              (status.percentage * 100).toFixed(1) + '%'
                             )
  var resStr =  `${nameStr} ${typeStr} ${sizeStr} ${percentageStr}`
  if(status.type == 'active'){
    var speedStr = ` ⬇️${bytesToReadable(status.downloadSpeed, 1)}/s`
     resStr += speedStr
  }
  return resStr
}
Promise.all([aria2.getGlobalStat(), aria2.tellActive(), aria2.tellWaiting(-1,10), aria2.tellStopped(-1,10)])
.then(([gStat, activeTasks, waitingTasks, stoppedTasks]) => {
  var activeTaskStatusList = activeTasks.map(genTaskStatus)
  var waitingTasksStatusList = waitingTasks.map(genTaskStatus)
  var stoppedTasksStatusList = stoppedTasks.map(genTaskStatus)
  var otherTasksStatusList = waitingTasksStatusList.concat(stoppedTasksStatusList)


  var bitbarContent = [
    {
      text: '💻  ⬇️ ' + bytesToReadable(gStat.downloadSpeed) + '/s'
    },
    bitbar.sep,
    {
      text: 'Active Tasks',
    },
    bitbar.sep
  ]

  // Active Tasks
  for(let item of activeTaskStatusList){
    bitbarContent.push(
      {
        text: taskStatusToString(item),
        font: 'Monaco'
      }
    )
  }

  bitbarContent.push(bitbar.sep)

  // Other Tasks
  bitbarContent.push(
    {
      text: 'Other Tasks'
    },
    bitbar.sep
  )
  for(let item of otherTasksStatusList){
    if(item){
      bitbarContent.push({
        text: taskStatusToString(item),
        font: 'Monaco'
      })
    }
  }

  bitbar(bitbarContent)
}).catch(err => {
   console.log(err)
})
