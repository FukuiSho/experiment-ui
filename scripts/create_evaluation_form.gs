function createEvaluationForm() {
  // 1. フォームの新規作成
  const form = FormApp.create('福井聖の応答評価テスト');
  form.setDescription('以下の発言（Query）に対して、どちらが「福井聖」らしい応答かを選択してください。');

  // 2. データの定義（JSON配列）
  const data = [
    {
        "id": "line:[LINE] Soraとのトーク.txt:14",
        "query": "何日がいい？",
        "generated_response": "27日午後で。他は無理。",
        "expected_response": "友達お金がなくて行けないって"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:18",
        "query": "5月1日はどう？",
        "generated_response": "五月一日は、何をするんや？",
        "expected_response": "チケットどうする？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:28",
        "query": "5月1日めっちゃ雨やからさ3日にしようや",
        "generated_response": "わかった。3日にする。",
        "expected_response": "マジか、でもワクチンやろ？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:18",
        "query": "5月1日はどう？",
        "generated_response": "イベント、オープニングやな。",
        "expected_response": "チケットどうする？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:28",
        "query": "5月1日めっちゃ雨やからさ3日にしようや",
        "generated_response": "あー、わかった。 3日にしとこう。",
        "expected_response": "マジか、でもワクチンやろ？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:58",
        "query": "時間は13:00くらい？",
        "generated_response": "お昼過ぎやんな。まぁそんな感じや。",
        "expected_response": "いいよ"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:76",
        "query": "なんでやねん笑笑",
        "generated_response": "え、どうした？急に笑笑。何か言いたいことある？",
        "expected_response": "いつやったら行けそう？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:79",
        "query": "了解",
        "generated_response": "お、了解。",
        "expected_response": "うちの友達は4、5やったら行けるってー"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:81",
        "query": "おっけい",
        "generated_response": "ええな、わかった。",
        "expected_response": "どうやった？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:87",
        "query": "誘っていいよ〜",
        "generated_response": "え、誘う？ あー、いいね！ どこか行きたいところある？ ボードゲームでもできれば最高やな！😊\n",
        "expected_response": "了解(笑)"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:97",
        "query": "こっちの方が安いな",
        "generated_response": "安いの、良いね。",
        "expected_response": "ルートはまた後でも大丈夫やろ多分、また詳しい友達に聞いてみるわ"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:98",
        "query": "ルートはまた後でも大丈夫やろ多分、また詳しい友達に聞いてみるわ",
        "generated_response": "うん、大丈夫や！焦らなくてええで。また聞けたら教えてや、多分なんとかなるやろ😁👍",
        "expected_response": "とりあえず明日最終決定しよ"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:104",
        "query": "5日の13:00にするか",
        "generated_response": "5日の13時でええわ。決定や。",
        "expected_response": "いいね"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:114",
        "query": "当日でいいよ",
        "generated_response": "当日、了解や。ええな。",
        "expected_response": "用意しとくように言っとくね"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:134",
        "query": "了解",
        "generated_response": "へえ、そうなん？",
        "expected_response": "何時からできそう？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:205",
        "query": "入るー",
        "generated_response": "まあ、好きにしろや。",
        "expected_response": "おけ"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:212",
        "query": "このメンバーでいつもやってるの？",
        "generated_response": "たまにね。\n\n\n\n---",
        "expected_response": "いつもは違うよ"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:234",
        "query": "そういえば、ドラクエXやらん？",
        "generated_response": "え、まじで？　たまにやるけどな。",
        "expected_response": "無料でできるんやって"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:267",
        "query": "ビンゴ！",
        "generated_response": "はい。\n\n\n\n---",
        "expected_response": "いいなー"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:272",
        "query": "なんかのクエストの報酬かも",
        "generated_response": "ふむ、**ご褒美か？** 面白えな。✨",
        "expected_response": "なんか光ってる樽にあるらしい"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:317",
        "query": "港町レンドアで",
        "generated_response": "港町か、へえ。\n",
        "expected_response": "了解"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:349",
        "query": "オレビンゴ",
        "generated_response": "へー、ビンゴね。\n\n\n\n---",
        "expected_response": "ビンゴってコインかかるの？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:419",
        "query": "16階おる",
        "generated_response": "へー、そうなんや。で？",
        "expected_response": "何かしてるの？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:453",
        "query": "オーキードーキー",
        "generated_response": "了解。まあ、別にいいや。",
        "expected_response": "画像はそっちで用意してて～"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:465",
        "query": "うん",
        "generated_response": "おもろいこと見つけて、楽しむのが一番やろ。",
        "expected_response": "じゃあどのタイミングでボスを出すかやな(笑)"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:471",
        "query": "ちょっとやることあるから10時スタートでいいかな？",
        "generated_response": "ええで、問題ないわ。",
        "expected_response": "うん"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:497",
        "query": "9月ごろちゃう？",
        "generated_response": "うん、そうかもな。9月か。🤔",
        "expected_response": "そんなもんか"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:505",
        "query": "その分大学でかまそうぜ",
        "generated_response": "あはは、せやな！ 大学、めっちゃ楽しもうぜ！ 勉強もサークルも、色々ぶっ壊して、最高に面白くかますわ！",
        "expected_response": "せやな！！"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:510",
        "query": "いてない",
        "generated_response": "へー、そうなんや。\n",
        "expected_response": "行ってないんかい(笑)"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:520",
        "query": "あとは、行ってたらローグライクのやり方サキヤと聞いてるやろうと思って聞きたかった",
        "generated_response": "あー、それね！サキヤさんからローグライクのやり方を聞いてるかな？と思ってたんだ。めっちゃ詳しいから、おすすめ聞くの正解だよ。\n\nどんなローグライクに興味ある？色々あるけど、サキヤさんは「Slay the Spire」とか「Binding of Isaac」とか、カードゲーム系とかも好きにしてるから、そういうのもおすすめできるかも。\n",
        "expected_response": "今日、バイト帰りに戦場行きたかったのに、鰻喰うから早く帰れって言わて行けへんし…(悔しい！！)"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:525",
        "query": "確か、アーケード初の放置ゲーって噂やで",
        "generated_response": "へー、マジで？面白そうやな。",
        "expected_response": "そうよな！聞いたことあるわ"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:536",
        "query": "ズゴック緑似合う",
        "generated_response": "え？ズゴックってガンダムの？緑色の服とかに合うってこと？ \n\nまあ、ちょっと意外な組み合わせやけど、俺も面白いもの好きやから、そこら辺スルーで行ってみるか！👍",
        "expected_response": "なぜだろう…これを見ていると、我主を思い出す…"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:545",
        "query": "アレ？ズゴックトゥルフ？",
        "generated_response": "ん？ガンダムちゃうの？",
        "expected_response": "(  -_・)?"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:551",
        "query": "どう？",
        "generated_response": "どうどう？って、なんか急だね！笑\n\nえっと、僕は福井聖、21歳だよ。大学3年生で、今はバイトしたりゲームしたり、結構ぐうたらしてるかな。好奇心旺盛ってところ、多分当てはまってると思う！ \n\n何か僕に聞きたいことある？",
        "expected_response": "画像がバグってただけちゃうかな？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:557",
        "query": "またねー",
        "generated_response": "おっけー！またねー！👋\n",
        "expected_response": "(笑)"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:567",
        "query": "戦場はガッツリやりたいから、別日にする",
        "generated_response": "え、戦場って？あ、ゲームの話ね！なるほど、ガッツリやる日は別に取っておくか。了解！\n",
        "expected_response": "分かった、金の準備しとけよ👍️"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:597",
        "query": "ええよ",
        "generated_response": "はーい、了解。\n進むで！",
        "expected_response": "わーい"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:621",
        "query": "せやねん",
        "generated_response": "ええな、わかった。",
        "expected_response": "９日やけど何時に集合する？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:622",
        "query": "９日やけど何時に集合する？",
        "generated_response": "午前やな。具体的な時間、まだ決まらん。",
        "expected_response": "昼から？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:627",
        "query": "了解",
        "generated_response": "お、まかせとけ。",
        "expected_response": "９日一時にnamco集合で！"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:641",
        "query": "しょうみ、まだやってないシナリオあるしな〜",
        "generated_response": "あー、ほんまやな。まだ時間あるし、ちょっと休憩して取り組むか！ボードゲームでもしながら頭切り替える？",
        "expected_response": "ならやめとくか"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:656",
        "query": "3階しか空いてないわ",
        "generated_response": "へー、そうなんや。\n",
        "expected_response": "行くか！"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:670",
        "query": "マジでな、でも、すぎやまこういちの指揮見たかったけどな…",
        "generated_response": "あー、すぎやまこういちさんの指揮ね。マジで聴きたかったっすよ！ファイナルファンタジーのコンサートとか、めちゃくちゃ憧れてたんですよねー。悔しいっす。",
        "expected_response": "惜しい人を失くした…"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:694",
        "query": "じゃあ13:30で！",
        "generated_response": "ええで、13:30やな。",
        "expected_response": "了解"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:704",
        "query": "35分くらいにつく",
        "generated_response": "35分？ ふむ…まー、なんとかなるか。",
        "expected_response": "了解"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:754",
        "query": "1日3回",
        "generated_response": "んな、アカンで。",
        "expected_response": "どんな内容か分からんけどいいと思うよ"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:801",
        "query": "遊ぶ",
        "generated_response": "え、遊ぶ？どこか行きたいとかある？ボードゲームでもする？😄\n",
        "expected_response": "どこで何しようか…(笑)"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:810",
        "query": "\"ごめん、寝落ちた。",
        "generated_response": "あー、いるいる！気にしすぎんな。俺もよくやるし。何か話してたっけ？\n",
        "expected_response": "どうする？どこにする？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:816",
        "query": "とりあえず、東梅田集合しよう",
        "generated_response": "ええな、わかったで。\n時間とか、具体的に？",
        "expected_response": "どこにする？"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:818",
        "query": "ビックエコー",
        "generated_response": "あー、良い店だね。🎤",
        "expected_response": "いっぱいあるやつやん(笑)"
    },
    {
        "id": "limitless:LJ0tbDcDPpWnGNvsojow:128",
        "query": "グレー の カプセル 分かる か な ?",
        "generated_response": "サプリメント？効果は人それぞれやろ。",
        "expected_response": "グレー の カプセル。"
    },
    {
        "id": "limitless:puH2rQ87KpoPOCjRifKw:338",
        "query": "あぶな。",
        "generated_response": "ん？何かあった？",
        "expected_response": "いやいやいや。"
    },
    {
        "id": "limitless:avi83tst1MziJYCHnW9U:862",
        "query": "え 、 しょう さん 行ける よ これ。",
        "generated_response": "ふむ、行けるか。  \nまあ、なんとかなるか。",
        "expected_response": "ええ 、 行け ん の?"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:2877",
        "query": "アサクリ新作の日本舞台のやつ、モバイルか！？",
        "generated_response": "はぇ、マジかよ？モバイル版アサシンクリード、日本舞台とかぶち上げすぎやんけ。\\\\\nオレはスマホゲーはあんまりやらないけど、これはチェックするわ。\\\\\n時代劇っぽいアサシンクリード、めっちゃワクワクするわ〜！",
        "expected_response": "モバイルなのは知らんかったわ(笑)"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:1631",
        "query": "一旦人数把握のTeams打とうかな",
        "generated_response": "おっけー、いいね！人数把握のTeams、回しておこう！誰がどれくらい集まるか、わかると動きやすいし。\n",
        "expected_response": "他の人が居ってもいいなら別に普通の予約でいけると思うよ。場所によって違うと思うけど…"
    },
    {
        "id": "limitless:yfKuvxNTm2O0qtsORemN:122",
        "query": "けど熊の過去がエグすぎて泣いてた。",
        "generated_response": "え、熊の過去！？あー、たしかにね…結構キツい話だったよね。マジで泣いちゃった？\n",
        "expected_response": "熊の？ いや、エッグヘッドはほんまに熊の過去は の話やでほんま。あれがメイン。"
    },
    {
        "id": "limitless:oswmonnSHZQUPPpCbdh0:395",
        "query": "え、分散パーソナルデータ構造化基盤によるチャットオートの本人再現。",
        "generated_response": "なるほどね、それってワクワクするな。",
        "expected_response": "ここで喋る。"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:4012",
        "query": "なんか、ITの学生は中田先生が打ち上げに連れて行くかも笑",
        "generated_response": "えっ、マジで？！中田先生、たまに突拍子もないこと言うからなぁ（笑）でも、打ち上げとか楽しそうじゃん！行くとしたら、どんなお店に連れてってくれるかなー。楽しみや！\n",
        "expected_response": "中田先生なんや(笑)"
    },
    {
        "id": "limitless:kRV4F9ENogfeS7dbNpCb:639",
        "query": "ああ 。",
        "generated_response": "そうだな、まあ、そうや。",
        "expected_response": "違う 。"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:1524",
        "query": "はーい",
        "generated_response": "お、どうした？",
        "expected_response": "明日行くやんな？"
    },
    {
        "id": "limitless:MxHtsU95DOhcTjKfZiUP:28",
        "query": "わから ん ご",
        "generated_response": "んー、ややこしいね。",
        "expected_response": "それ は ちょっと ボケット し てる か も な"
    },
    {
        "id": "limitless:kRV4F9ENogfeS7dbNpCb:232",
        "query": "ナイス 。",
        "generated_response": "へえ、そうやな。",
        "expected_response": "ま 何 やっ た ?"
    },
    {
        "id": "limitless:oswmonnSHZQUPPpCbdh0:348",
        "query": "あ、そう。",
        "generated_response": "ふむ、それで？",
        "expected_response": "そんな真面目に考える。"
    },
    {
        "id": "limitless:8UnB1cfOQGaixnM9Ws8j:74",
        "query": "これ。",
        "generated_response": "ふむ、なんとなく分かった。",
        "expected_response": "いいな。"
    },
    {
        "id": "limitless:VTr42AH1bGIubMkAXsvk:195",
        "query": "そう な ん よ 。",
        "generated_response": "せやな、それでええやん。",
        "expected_response": "なるほど な 。"
    },
    {
        "id": "limitless:puH2rQ87KpoPOCjRifKw:658",
        "query": "何やってんな。",
        "generated_response": "オレ、世界平和を目指してる。",
        "expected_response": "なんか佐藤健さんのいいよ。"
    },
    {
        "id": "line:[LINE] Soraとのトーク.txt:1334",
        "query": "団体割引あるらしい",
        "generated_response": "へえ、お得やな😲",
        "expected_response": "みんなと要相談やな"
    },
    {
        "id": "limitless:kRV4F9ENogfeS7dbNpCb:763",
        "query": "え?",
        "generated_response": "ん？何か聞きたいか？",
        "expected_response": "え?"
    },
    {
        "id": "limitless:UJvehVH6vSaiAcO8zW3w:9",
        "query": "筋トレ し た。",
        "generated_response": "ええね。継続が大事やで。",
        "expected_response": "セリ。"
    },
    {
        "id": "limitless:avi83tst1MziJYCHnW9U:782",
        "query": "ああ 、 何これ?",
        "generated_response": "自己紹介文やな。オレのこと。",
        "expected_response": "ほんま に ある の か?"
    }
];

  data.forEach((item, index) => {
    // 質問セクションの作成
    // タイトルにQuery（質問内容）を表示
    const itemTitle = `Q${index + 1}. 問い: 「${item.query}」`;
    const mcItem = form.addMultipleChoiceItem();
    
    // ランダムに配置するために選択肢をシャッフル
    const choices = [
      { type: 'generated', value: item.generated_response },
      { type: 'expected', value: item.expected_response }
    ];
    // Fisher-Yates shuffle
    for (let i = choices.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [choices[i], choices[j]] = [choices[j], choices[i]];
    }

    mcItem.setTitle(itemTitle)
          //.setHelpText(`データID: ${item.id}`) // IDは削除
          .setChoices([
            mcItem.createChoice(choices[0].value),
            mcItem.createChoice(choices[1].value)
          ])
          .setRequired(true); // 回答必須にする場合
  });

  console.log('フォーム作成が完了しました。');
  console.log('編集用URL: ' + form.getEditUrl());
  console.log('公開用URL: ' + form.getPublishedUrl());
}
