#include <eosio/eosio.hpp>
using namespace eosio;

struct [[eosio::table("message"), eosio::contract("talk")]] message {
   uint64_t id = {};
   uint64_t reply_to = {};
   eosio::name user = {};
   std::string content = {};

   uint64_t primary_key() const { return id; }
   uint64_t get_reply_to() const { return reply_to; }
};

CONTRACT talk : public contract {
   public:
      using contract::contract;

      ACTION post( uint64_t id, uint64_t reply_to, eosio::name user, const std::string& content);
   
      using message_table = eosio::multi_index<
         "message"_n, message, eosio::indexed_by<"by.reply.to"_n, eosio::const_mem_fun<message, uint64_t, &message::get_reply_to>>>;

      using post_action = action_wrapper<"post"_n, &talk::post>;
};