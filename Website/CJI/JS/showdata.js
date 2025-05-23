async function fetchdata()   //异步获取数据函数 
{
    try {
        const response = await fetch("http://192.168.4.2:5500/get_data");  //发送HTTP请求到ESP01S
        const data = await response.json();  //等待服务器响应，并将结果解析为json格式
        const list = document.getElementById("data-list");  //更新原网页sensordata的值

        // 清空列表，初始化列表
        list.innerHTML = '';
        //遍历数据并动态插入
        if (Array.isArray(data)) {
            data.forEach(item => {
                const li = document.createElement('li');   //li为ul里面的元素形式
                li.textContent = `时间: ${item.time}, 温度: ${item.Temp}℃, 湿度: ${item.RH}%`;
                list.appendChild(li);
            });
        }
        else {
            console.error("数据不是数组格式", data)
        }
    }
    catch (error) {
        console.error("无法获得数据：", error)
    }
}


//函数2
function compare_data(formID, inputID) {
    //获取表单
    const form = document.getElementById(formID);
    //获取数据
    const inputs = inputID.map(id => document.getElementById(id));    //map() 是 JavaScript 数组的方法，它用于对数组的每个元素执行回调函数，并返回一个新的数组。
    let flag_data = true;   //用于数据判定。优化：之前是放在空格监听事件里面，但会出现submit重复绑定，这次将它放到外面来。 优化1:由于删掉了表单绑定部分，这个参数也就无效了
    let all = false;        //此处是故意设为初始值false，防止万一都没进验证就直接过关

    //绑定检测事件
    inputs.forEach(input => input.addEventListener("blur", function () {
        //之前由于仅简简单单的绑定表单提交，导致之后出错，无法进入第二次的监听表单部分，导致会错误，但是一直停留在第一次报错的错误
        //更改第二次，将表单的监听移除出来，单独的在最后提交部分进行表单的监听。原来外面的表单监听则改为移出来的inputs的第四个输入的光标移出
        //第三次更改，对inputs的每一个元素input都进行光标的移出判定，从而能更好地单独对每个不符合要求的输入框进行警示

        let pos = [0, 0, 0, 0];  //用于判定的先后

        const values = inputs.map(input => parseInt(input.value));   //转为整形数据

        //清除之前的异况
        inputs.forEach(input => input.setCustomValidity(""));

        //检验1：是否为整数
        values.forEach((value, index) => {
            if (!Number.isInteger(value)) {
                inputs[index].setCustomValidity("请输入整数");
                pos[index] = 1;   //对每个值判定
            }
            else {
                inputs[index].setCustomValidity("");
                pos[index] = 0;
            }
        });
        //对上面的判定数组的每个数值进行分析
        all = pos.every(value => value == 0);    //如果每个值都为0，则返回true
        //if (!all) {
        //    flag_data = false;
        //}

        //检测2：上限是否大于下限
        if (all) {
            if (values[1] >= values[0]) {   //当出现错误：最低温度>最高温度
                inputs[1].setCustomValidity("此处为最低温度阈值，要小于最高温度阈值");
                flag_data = false;
            } else {
                inputs[1].setCustomValidity("");
            }
            if (values[3] >= values[2]) {
                inputs[3].setCustomValidity("此处为最低湿度阈值，要小于最高湿度阈值");
                flag_data = false;
            } else {
                inputs[3].setCustomValidity("");
            }
        }
    }));    //这里面的两个括号说明下：第一个：是监听光标移除事件的；第二个：对于inputs的元素遍历的括号
    if (flag_data && all) {
        form.addEventListener("submit", function () {
            alert("数据验证成功，正在提交.....");
        });
    }
    //绑定表单提交事件。  优化0：将原本镶嵌到里面的表单提交函数分离出来。优化1：直接将这一块删了，因为setCustomValidity只要没删掉，表单就交不了的
    //form.addEventListener("submit", function (event) {
    //根据判定来判断是否提交表单
    //    if (!flag_data) {
    //        event.preventDefault();
    //        inputs.forEach(input => input.setCustomValidity(""));
    //    } else {
    //        alert("数据验证成功，正在提交.....");
    //    }
    //});
}


window.onload = () => {
    fetchdata();
    compare_data('data-form', ['TH', 'TL', 'RH', 'RL']);  //比较温度输入框
}
//第一个函数是从后端数据库读取温湿度数据
//第二个函数是对于输入温湿度阈值的比较判定提示