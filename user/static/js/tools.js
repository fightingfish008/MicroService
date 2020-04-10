String.prototype.format = function () {
    let args = Array.prototype.slice.call(arguments);
    let count = 0;
    return this.replace(/{}/g, function (s, i) {
        return args[count++];
    });
};


function Base64() {

    // private property
    _keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

    // public method for encoding
    this.encode = function (input) {
        let output = "";
        let chr1, chr2, chr3, enc1, enc2, enc3, enc4;
        let i = 0;
        input = _utf8_encode(input);
        while (i < input.length) {
            chr1 = input.charCodeAt(i++);
            chr2 = input.charCodeAt(i++);
            chr3 = input.charCodeAt(i++);
            enc1 = chr1 >> 2;
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
            enc4 = chr3 & 63;
            if (isNaN(chr2)) {
                enc3 = enc4 = 64;
            } else if (isNaN(chr3)) {
                enc4 = 64;
            }
            output = output +
                _keyStr.charAt(enc1) + _keyStr.charAt(enc2) +
                _keyStr.charAt(enc3) + _keyStr.charAt(enc4);
        }
        return output;
    };

    // public method for decoding
    this.decode = function (input) {
        let output = "";
        let chr1, chr2, chr3;
        let enc1, enc2, enc3, enc4;
        let i = 0;
        input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        while (i < input.length) {
            enc1 = _keyStr.indexOf(input.charAt(i++));
            enc2 = _keyStr.indexOf(input.charAt(i++));
            enc3 = _keyStr.indexOf(input.charAt(i++));
            enc4 = _keyStr.indexOf(input.charAt(i++));
            chr1 = (enc1 << 2) | (enc2 >> 4);
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
            chr3 = ((enc3 & 3) << 6) | enc4;
            output = output + String.fromCharCode(chr1);
            if (enc3 !== 64) {
                output = output + String.fromCharCode(chr2);
            }
            if (enc4 !== 64) {
                output = output + String.fromCharCode(chr3);
            }
        }
        output = _utf8_decode(output);
        return output;
    };

    // private method for UTF-8 encoding
    _utf8_encode = function (string) {
        string = string.replace(/\r\n/g, "\n");
        let utftext = "";
        for (let n = 0; n < string.length; n++) {
            let c = string.charCodeAt(n);
            if (c < 128) {
                utftext += String.fromCharCode(c);
            } else if ((c > 127) && (c < 2048)) {
                utftext += String.fromCharCode((c >> 6) | 192);
                utftext += String.fromCharCode((c & 63) | 128);
            } else {
                utftext += String.fromCharCode((c >> 12) | 224);
                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                utftext += String.fromCharCode((c & 63) | 128);
            }

        }
        return utftext;
    };

    // private method for UTF-8 decoding
    _utf8_decode = function (utftext) {
        let string = "";
        let i = 0;
        let c = c1 = c2 = 0;
        while (i < utftext.length) {
            c = utftext.charCodeAt(i);
            if (c < 128) {
                string += String.fromCharCode(c);
                i++;
            } else if ((c > 191) && (c < 224)) {
                c2 = utftext.charCodeAt(i + 1);
                string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
                i += 2;
            } else {
                c2 = utftext.charCodeAt(i + 1);
                c3 = utftext.charCodeAt(i + 2);
                string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
                i += 3;
            }
        }
        return string;
    }
}

function Stack() {

    let items = [];

    this.push = function (element) {
        items.push(element);
    };

    this.pop = function () {
        return items.pop();
    };

    this.peek = function () {
        return items[items.length - 1];
    };

    this.isEmpty = function () {
        return items.length === 0;
    };

    this.size = function () {
        return items.length;
    };

    this.clear = function () {
        items = [];
    };

    this.print = function () {
        console.log(items.toString());
    };

    this.toString = function () {
        return items.toString();
    };
}

let getUrlParam = function (name) {
    let reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    let r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]);
    return null;
};

let getDate = function (delay) {
    delay = delay || 0;
    let date = new Date();
    date.setDate(date.getDate() + delay);//获取AddDayCount天后的日期
    let y = date.getFullYear();
    let m = date.getMonth() + 1;
    m = m < 10 ? '0' + m : m;
    let d = date.getDate();
    d = d < 10 ? ('0' + d) : d;
    return y + '-' + m + '-' + d;
};

// (function (window, document) {
//     let currentPosition = 0; //记录当前页面位置
//     let currentPoint = -1;   //记录当前点的位置
//     let pageNow = 1;   //当前页码
//     let points = null; //页码数
//
//     let app = {
//         init: function () {
//             document.addEventListener('DOMContentLoaded', function () {
//                 points = document.querySelectorAll('.pagenumber div');
//                 app.bindTouchEvent(); //绑定触摸事件
//                 // app.bindBtnClick();   //绑定按钮点击事件
//                 // app.setPageNow();     //设置初始页码
//             }.bind(app), false);
//         }(),
//
//
//         // bindBtnClick: function () {
//         //     let button = document.querySelector('#testbtn');
//         //     button.addEventListener('touchstart', function () {
//         //         console.log('touch')
//         //     })
//         //
//         // },
//
//
//         //页面平移
//         transform: function (translate) {
//             this.style.webkitTransform = "translate3d(" + translate + "px,0,0)";
//             currentPosition = translate;
//
//         },
//
//         // /**
//         //  * 设置当前页码
//         //  */
//         // setPageNow: function () {
//         //     if (currentPoint !== -1) {
//         //         points[currentPoint].className = '';
//         //     }
//         //     currentPoint = pageNow - 1;
//         //     points[currentPoint].className = 'now';
//         // },
//
//         /**
//          * 绑定触摸事件
//          */
//         bindTouchEvent: function () {
//             let viewport = document.querySelector('#main');
//             let pageWidth = window.innerWidth; //页面宽度
//             let maxWidth = -pageWidth * (points.length - 1); //页面滑动最后一页的位置
//             let startX, startY;
//             let initialPos = 0;  // 手指按下的屏幕位置
//             let moveLength = 0;  // 手指当前滑动的距离
//             let direction = "left"; //滑动的方向
//             let isMove = false; //是否发生左右滑动
//             let startT = 0; //记录手指按下去的时间
//             let isTouchEnd = true; //标记当前滑动是否结束(手指已离开屏幕)
//
//             /*手指放在屏幕上*/
//             document.addEventListener("touchstart", function (e) {
//                 // e.preventDefault();
//                 //单手指触摸或者多手指同时触摸，禁止第二个手指延迟操作事件
//                 if (e.touches.length === 1 || isTouchEnd) {
//                     let touch = e.touches[0];
//                     startX = touch.pageX;
//                     startY = touch.pageY;
//                     initialPos = currentPosition;   //本次滑动前的初始位置
//                     viewport.style.webkitTransition = ""; //取消动画效果
//                     startT = new Date().getTime(); //记录手指按下的开始时间
//                     isMove = false; //是否产生滑动
//                     isTouchEnd = false; //当前滑动开始
//                 }
//             }.bind(this), false);
//
//             /*手指在屏幕上滑动，页面跟随手指移动*/
//             document.addEventListener("touchmove", function (e) {
//                 e.preventDefault();
//
//                 //如果当前滑动已结束，不管其他手指是否在屏幕上都禁止该事件
//                 if (isTouchEnd) return;
//
//                 let touch = e.touches[0];
//                 let deltaX = touch.pageX - startX;
//                 let deltaY = touch.pageY - startY;
//                 //如果X方向上的位移大于Y方向，则认为是左右滑动
//                 if (Math.abs(deltaX) > Math.abs(deltaY)) {
//                     moveLength = deltaX;
//                     let translate = initialPos + deltaX; //当前需要移动到的位置
//                     //如果translate>0 或 < maxWidth,则表示页面超出边界
//                     if (translate <= 0 && translate >= maxWidth) {
//                         this.transform.call(viewport, translate);
//                         isMove = true;
//                     }
//                     direction = deltaX > 0 ? "right" : "left"; //判断手指滑动的方向
//                 }
//
//             }.bind(this), false);
//
//             /*手指离开屏幕时，计算最终需要停留在哪一页*/
//             document.addEventListener("touchend", function (e) {
//                 // e.preventDefault();
//                 let translate = 0;
//                 //计算手指在屏幕上停留的时间
//                 let deltaT = new Date().getTime() - startT;
//                 //发生了滑动，并且当前滑动事件未结束
//                 if (isMove && !isTouchEnd) {
//                     isTouchEnd = true; //标记当前完整的滑动事件已经结束
//
//                     //使用动画过渡让页面滑动到最终的位置
//                     viewport.style.webkitTransition = "0.3s ease -webkit-transform";
//                     if (deltaT < 300) { //如果停留时间小于300ms,则认为是快速滑动，无论滑动距离是多少，都停留到下一页
//                         translate = direction === 'left' ?
//                             currentPosition - (pageWidth + moveLength) : currentPosition + pageWidth - moveLength;
//                         //如果最终位置超过边界位置，则停留在边界位置
//                         translate = translate > 0 ? 0 : translate; //左边界
//                         translate = translate < maxWidth ? maxWidth : translate; //右边界
//                     } else {
//                         //如果滑动距离小于屏幕的50%，则退回到上一页
//                         if (Math.abs(moveLength) / pageWidth < 0.5) {
//                             translate = currentPosition - moveLength;
//                         } else {
//                             //如果滑动距离大于屏幕的50%，则滑动到下一页
//                             translate = direction === 'left' ?
//                                 currentPosition - (pageWidth + moveLength) : currentPosition + pageWidth - moveLength;
//                             translate = translate > 0 ? 0 : translate;
//                             translate = translate < maxWidth ? maxWidth : translate;
//                         }
//                     }
//
//                     //执行滑动，让页面完整的显示到屏幕上
//                     this.transform.call(viewport, translate);
//                     //计算当前的页码
//                     pageNow = Math.round(Math.abs(translate) / pageWidth) + 1;
//
//                     setTimeout(function () {
//                         //设置页码，DOM操作需要放到异步队列中，否则会出现卡顿
//                         this.setPageNow();
//                     }.bind(this), 100);
//                 }
//             }.bind(this), false);
//         }
//     }
// })(window, document);
