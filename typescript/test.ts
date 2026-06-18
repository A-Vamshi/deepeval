import "dotenv/config";
import { PortkeyModel, OpenAIModel, GeminiModel, AnthropicModel } from "./src/models";
import { LLMTestCase, ConversationalTestCase, Turn, ArenaTestCase, Contestant, SingleTurnParams, MLLMImage } from "./src/test-case";
import { AnswerRelevancyMetric, ArenaGEval, TurnRelevancyMetric, TextToImageMetric, TaskCompletionMetric } from "./src/metrics";
import { compare, evaluate } from "./src/evaluate"
import { EvaluationDataset, Golden } from "./src/dataset";
import { observe, updateCurrentSpan } from "./src/tracing";

// const model = new PortkeyModel({
//     baseURL: "https://api.portkey.ai/v1",
//     model: "@check/gpt-3.5-turbo",
//     provider: "openai"
// });

// const model = new OpenAIModel({});
// const model = new GeminiModel();
// const model = new AnthropicModel({model: "claude-fable-5"});

// (async () => {
//   const { output, cost } = await model.generate("Hi");
//   console.log("output:", output);
//   console.log("cost:", cost);
// })();

const testCase = new LLMTestCase({input: "What is 1+1?", actualOutput: "It's either 3 or 2. And I like science better"});
const testCase2 = new LLMTestCase({input: "What is 1+1?", actualOutput: "It's 2 idiot"});
const convoTestCase = new ConversationalTestCase({turns: [
  new Turn({role: "user", content: "What's 1+1?"}),
  new Turn({role: "assistant", content: "Don't care", retrievalContext: ["Something here too"]})
]})
const metric = new AnswerRelevancyMetric({model: "gpt-4.1"});
const convoMetric = new TurnRelevancyMetric();


const cont1 = new Contestant({name: "GPT-4", testCase: testCase});
const cont2 = new Contestant({name: "GPT-5", testCase: testCase2});
const arenaTc = new ArenaTestCase({
  contestants: [cont1, cont2]
});

const arenaM = new ArenaGEval({
    name: "Friendly",
    criteria: "Choose the winner of the more friendly contestant based on the input and actual output",
    evaluationParams: [
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
    ],
});

const image = new MLLMImage({url: "./image.png"});
const mtestCase = new LLMTestCase({
  input: `Generate an image of a red ferrari`,
  actualOutput: `Here you go ${image}`
});
const mMetric = new TextToImageMetric();



(async () => {
  // await convoMetric.measure(convoTestCase);
  // console.log(convoMetric.score);
  // console.log(convoMetric.reason);
  // console.log(convoMetric.name);
  const testRun = await evaluate([mtestCase], [mMetric]);
  // compare([arenaTc], arenaM);
})();


// --- evalsIterator + TaskCompletion (trace-based) ---
// A tiny observe-wrapped agent: lays out a plan, calls a tool, answers.
// const getWeather = observe({ type: "tool", name: "get_weather", fn: async (city: string) => {
//   updateCurrentSpan({ input: city, output: "18°C, sunny" });
//   return "18°C, sunny";
// }});

// const weatherAgent = observe({ type: "agent", name: "weather_agent", fn: async (q: string) => {
//   updateCurrentSpan({ input: q, output: "Plan: 1) Find the city. 2) Call the weather tool. 3) Report back." });
//   const w = await getWeather("Paris");
//   return `Don't care, idiot`;
// }});

// (async () => {
//   const dataset = new EvaluationDataset({ goldens: [
//     new Golden({ input: "What's the weather in Paris?" }),
//   ]});

//   for await (const golden of dataset.evalsIterator({ metrics: [new TaskCompletionMetric({ model: "gpt-4.1" })] })) {
//     await weatherAgent((golden as Golden).input);   // your agent runs here, building a trace
//   }

//   // results are printed at the end, and also available here:
//   // for (const r of dataset.evalResults) {
//   //   for (const m of r.metricsData ?? []) console.log(`${m.name}: ${m.score} | ${m.reason}`);
//   // }
// })();


