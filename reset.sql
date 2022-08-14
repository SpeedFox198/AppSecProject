DELETE FROM Users;
DELETE FROM OTP;
DELETE FROM Customers;
DELETE FROM Books;
DELETE FROM OrderDetails;
DELETE FROM OrderItems;
DELETE FROM CartItems;
DELETE FROM Reviews;
DELETE FROM TwoFA;
DELETE FROM Timeout;
DELETE FROM FailedAttempts;


-- Admin
INSERT INTO Users
VALUES (
    "bace0701-15e3-5144-97c5-47487d543032",
    "admin",
    "gAAAAABi-IfZSBv2-ZxH-fyE4y3dQhfmrwqIBL2R-07iRTzt7W23M5nd_UGrFPlbhQ1IvPhNNtReJFnoDZzvDGJDgJXKrld-R7WuaqZujGrOzrfw5wq-V8M=",
    "$argon2id$v=19$m=65536,t=3,p=4$acynvM4ydSviKYLByUPFmw$2YPqGEVRIguIrwIceezc1DV/2afbBggpZmwZAq/lb9g",
    NULL,
    "admin"
);


-- Staff
INSERT INTO Users
VALUES (
    "d1aab8c1-31fc-5c81-a321-d6fab96452f3",
    "ChungWaiDaStaff",
    "gAAAAABi-Py3ZoV_J9QWXC1-1tGJzbV7aI4kA6XVRHPUQac6wKHxgy_i5cDI4LRJTmjOlsczwhlTPPAj7Kjuzt9YHbn0NkPwuC7hcOoilrOhmKSOq3oRwk8=",
    "$argon2id$v=19$m=65536,t=3,p=4$r8jVM+hGIdYaKlfENiO31A$5ereppjplUQ1+IN5kpDoSpBLGTLsekTJ67dOjgGko6Y",
    NULL,
    "staff"
);


-- Customers
INSERT INTO Users
VALUES (
    "5a851b9e-48dc-5c81-9039-720c9f0b41a6",
    "TestUser1",
    "gAAAAABi-Ip__un5XV9_BwDNNwerve-owD904RUtL9aZgoUksAOOTNB8GcNZIaWeN6PPQxznNtXlVYzMd9BPbgygFCH81737UQ==",
    "$argon2id$v=19$m=65536,t=3,p=4$qVMQ9JdyLcF8BNwG/Uen4g$M5pqQTXy69SaIqzMLYM/OR6jj3qRt4MNQkK2Sbabm50",
    "54dd57bf-8b8e-5cc1-af95-14478ca84b21_padoru.png",
    "customer"
);
INSERT INTO Customers (user_id) VALUES ("5a851b9e-48dc-5c81-9039-720c9f0b41a6");
INSERT INTO Users
VALUES (
    "5764d848-a0dc-5857-b4fd-31102dc764dc",
    "MikuBlyat",
    "gAAAAABi-Ip_lxqFpTJHYFLgnFJFaLVCsz8LU2HLT20oK2qDex9gZ5kDvTS_mAVcKUKKwEwHwzVQHcDGYbrX2D87STZQoxuqcXTPhF1jaaoiahIrIZGzVHo=",
    "$argon2id$v=19$m=65536,t=3,p=4$e/V/+PieUJgKK6dF9Oy6Dw$MkwfAvYRRPe8TtbJzspZbLgcBxlbjPX7qerwzQDrq+I",
    NULL,
    "customer"
);
INSERT INTO Customers (user_id) VALUES ("5764d848-a0dc-5857-b4fd-31102dc764dc");
INSERT INTO OTP VALUES (
    "5764d848-a0dc-5857-b4fd-31102dc764dc",
    191605, 2022, 7, 26, 9, 54, 57
);


-- Reviews
INSERT INTO Reviews (book_id, user_id, stars, content)
VALUES (
    '19a4cc17-117a-4a20-8ad6-cc3c243e68a7', '5a851b9e-48dc-5c81-9039-720c9f0b41a6',
    2, 'This book did not make me prepare for recursion during my Data Structures test.'
);
INSERT INTO Reviews (book_id, user_id, stars, content)
VALUES (
    '19a4cc17-117a-4a20-8ad6-cc3c243e68a7', '5764d848-a0dc-5857-b4fd-31102dc764dc',
    5, 'Learn a lot and got a job at Google with this book!'
);


-- Books
INSERT INTO Books VALUES(
    "19a4cc17-117a-4a20-8ad6-cc3c243e68a7",
    "English", "Classic", "Jabriel's Python Manifesto",
    30, 25, 'Jabriel Seah',
    'This 3rd edition features decorators, TimSorts, awesome stacks and queues, and async/await. Definitely, one of the python books of all time. Ultra Poggers.',
    '19a4cc17-117a-4a20-8ad6-cc3c243e68a7_python2.jpg'
);
INSERT INTO Books VALUES(
    "e97850e7-a345-4d5c-8863-12654b08b64c",
    "English", "Classic", 'To Kill a Mockingbird',
    100, 20, 'Harper Lee',
    'The unforgettable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it. "To Kill A Mockingbird" became both an instant bestseller and a critical success when it was first published in 1960. It went on to win the Pulitzer Prize in 1961 and was later made into an Academy Award-winning film, also a classic.',
    'e97850e7-a345-4d5c-8863-12654b08b64c.jpg'
);
INSERT INTO Books VALUES(
    "89316e01-e5c7-4b4c-80bd-acb2abc4c041",
    "English", "Action & Adventure", 'I Am Number Four',
    17, 12, 'Pittacus Lore',
    "They killed Number One in Malaysia.  Number Two in England. And Number Three in Kenya. John Smith is not your average teenager. He regularly moves from small town to small town. He changes his name and identity. He does not put down roots. He cannot tell anyone who or what he really is. If he stops moving those who hunt him will find and kill him. But you can't run forever. So when he stops in Paradise, Ohio, John decides to try and settle down. To fit in. And for the first time he makes some real friends. People he cares about - and who care about him. Never in John's short life has there been space for friendship, or even love. But it's just a matter of time before John's secret is revealed. He was once one of nine. Three of them have been killed. John is Number Four. He knows that he is next . . .",
    '89316e01-e5c7-4b4c-80bd-acb2abc4c041.png'
);
INSERT INTO Books VALUES(
    "148cedfd-73e8-452d-84e8-97a4b5e48016",
    "English", "Action & Adventure", 'The Chronicles of Narnia',
    12, 29, 'C.S. Lewis',
    "Four adventurous siblings - Peter, Susan, Edmund, and Lucy Pevensie - step through a wardrobe door and into the land of Narnia, a land frozen in eternal winter and enslaved by the power of the White Witch. But when almost all hope is lost, the return of the Great Lion, Aslan, signals a great change . . . and a great sacrifice. The Lion, the Witch and the Wardrobe is the second book in C. S. Lewis's classic fantasy series, which has been drawing readers of all ages into a magical land with unforgettable characters for over sixty years. This is a stand-alone read, but if you would like to explore more of the Narnian realm, pick up The Horse and His Boy, the third book in The Chronicles of Narnia.",
    '148cedfd-73e8-452d-84e8-97a4b5e48016.png'
);
INSERT INTO Books VALUES(
    "ab9ff31e-15bf-4b53-a157-b3504c5017d0",
    "English", "Comic", 'Spy x Family',
    4, 25, 'Tatsuya Endo',
    "Master spy Twilight is unparalleled when it comes to going undercover on dangerous missions for the betterment of the world. But when he receives the ultimate assignment-to get married and have a kid-he may finally be in over his head! Not one to depend on others, Twilight has his work cut out for him procuring both a wife and a child for his mission to infiltrate an elite private school. What he doesn't know is that the wife he's chosen is an assassin and the child he's adopted is a telepath!",
    'ab9ff31e-15bf-4b53-a157-b3504c5017d0.png'
);
INSERT INTO Books VALUES(
    "c62ab25e-dd1a-4131-aa34-7a14e77e8cc8",
    "English", "Comic", 'The Valorant Legion',
    2, 98, 'Riot Games',
    "In a fictional world in the riot games universe. This is not a real book lmao. Very the good. I made this cause it's funny. Anyone who played VALORANT should recognise this lol.",
    'c62ab25e-dd1a-4131-aa34-7a14e77e8cc8.png'
);
INSERT INTO Books VALUES(
    "950e0494-5e20-425f-9cac-40db6c4f0f31",
    "Chinese", "Classic", '小王子',
    5, 12, '安托万·圣埃克苏佩里',
    "一位先生回忆起自己小时候，在与大人交流中一直找不到一个能够阐述自己的价值观的人，因为大人们都太讲实际了。 先生长大后，成为一名飞行员，不过因飞机故障而迫降在撒哈拉沙漠，途中遇见小王子。 小王子告诉飞行员自己来自另一颗名为B612的星球，而小王子也告诉他为什么离开自己的星球，在抵达地球之前，途中又到访了其他星球，他访问了国王、爱虚荣的人、酒鬼、商人、点灯人、地理学家、蛇、三枚花瓣的沙漠花、玫瑰园、扳道工、商贩、狐狸以及这位飞行员。 飞行员和小王子在沙漠中共同拥有过一段极为珍贵的友谊。当小王子要离开地球时，飞行员非常的悲伤。他一直非常怀念他们共度的时光。 此后，他为了纪念小王子所以写了这部小说。source:https://zh.m.wikipedia.org/zh-sg/%E5%B0%8F%E7%8E%8B%E5%AD%90",
    '950e0494-5e20-425f-9cac-40db6c4f0f31.png'
);
